import os
import uuid
import tempfile
from typing import List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.auth import get_current_user
from app.core.database import get_supabase_client
from app.models.user import User
from app.models.analysis import AnalysisCreate, AnalysisResponse
from app.services.video_processor import VideoProcessor
from app.services.pose_estimator import PoseEstimator
from app.services.rep_counter import RepCounter
from app.services.ai_analyzer import AIAnalyzer
from app.services.usage_tracker import UsageTracker
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(
    video: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a workout video and return form assessment
    """
    try:
        # Validate file
        if not video.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size
        if video.size and video.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Check file type
        file_extension = video.filename.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File type not supported. Allowed types: {', '.join(settings.ALLOWED_VIDEO_TYPES)}"
            )
        
        # Check user usage limits
        usage_tracker = UsageTracker()
        daily_usage = await usage_tracker.get_daily_usage(current_user.id)
        
        if current_user.subscription_status != "pro" and daily_usage >= settings.FREE_DAILY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Daily analysis limit reached. Please upgrade to Pro for unlimited analyses."
            )
        
        # Track analysis start
        analytics = AnalyticsService()
        await analytics.track_event(
            "analysis_started",
            user_id=current_user.id,
            properties={
                "file_size": video.size,
                "file_type": file_extension,
                "subscription_status": current_user.subscription_status,
            }
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await video.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Initialize services
            video_processor = VideoProcessor()
            pose_estimator = PoseEstimator()
            rep_counter = RepCounter()
            ai_analyzer = AIAnalyzer()
            
            # Process video and extract frames
            logger.info(f"Processing video for user {current_user.id}")
            frames = await video_processor.extract_frames(temp_file_path)
            
            if not frames:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not extract frames from video"
                )
            
            # Extract pose keypoints
            logger.info("Extracting pose keypoints")
            keypoints_data = []
            for i, frame in enumerate(frames):
                keypoints = await pose_estimator.extract_pose(frame)
                if keypoints:
                    keypoints_data.append({
                        "frame": i,
                        "keypoints": keypoints,
                        "timestamp": i / len(frames)  # Approximate timestamp
                    })
            
            if not keypoints_data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not detect pose in video"
                )
            
            # Count repetitions
            logger.info("Counting repetitions")
            rep_count, exercise_type = await rep_counter.count_reps(keypoints_data)
            
            # Analyze form with AI
            logger.info("Analyzing form with AI")
            ai_analysis = await ai_analyzer.analyze_form(
                keypoints_data=keypoints_data,
                exercise_type=exercise_type,
                rep_count=rep_count
            )
            
            # Create analysis record
            analysis_data = AnalysisCreate(
                user_id=current_user.id,
                video_filename=video.filename,
                exercise_type=exercise_type,
                form_score=ai_analysis["score"],
                rep_count=rep_count,
                risks=ai_analysis["risks"],
                corrections=ai_analysis["corrections"],
                keypoints_data=keypoints_data,
            )
            
            # Save to database
            supabase = get_supabase_client()
            result = supabase.table("analyses").insert(analysis_data.dict()).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save analysis"
                )
            
            analysis_id = result.data[0]["id"]
            
            # Update usage
            await usage_tracker.increment_daily_usage(current_user.id)
            
            # Track successful analysis
            await analytics.track_event(
                "analysis_completed",
                user_id=current_user.id,
                properties={
                    "analysis_id": analysis_id,
                    "exercise_type": exercise_type,
                    "score": ai_analysis["score"],
                    "rep_count": rep_count,
                    "subscription_status": current_user.subscription_status,
                }
            )
            
            # Prepare response
            response_data = AnalysisResponse(
                id=analysis_id,
                exercise=exercise_type,
                score=ai_analysis["score"],
                risks=ai_analysis["risks"],
                corrections=ai_analysis["corrections"],
                rep_count=rep_count,
                created_at=datetime.utcnow(),
            )
            
            logger.info(f"Analysis completed successfully for user {current_user.id}")
            return response_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error for user {current_user.id}: {str(e)}")
        
        # Track failed analysis
        analytics = AnalyticsService()
        await analytics.track_event(
            "analysis_failed",
            user_id=current_user.id,
            properties={
                "error": str(e),
                "file_size": video.size if video.size else 0,
                "file_type": video.filename.split('.')[-1].lower() if video.filename else "unknown",
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again."
        )

@router.get("/analyses", response_model=List[AnalysisResponse])
async def get_user_analyses(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    """
    Get user's analysis history
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("analyses") \
            .select("*") \
            .eq("user_id", current_user.id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        analyses = []
        for row in result.data:
            analyses.append(AnalysisResponse(**row))
        
        return analyses
    
    except Exception as e:
        logger.error(f"Error fetching analyses for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analyses"
        )

@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get specific analysis by ID
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("analyses") \
            .select("*") \
            .eq("id", analysis_id) \
            .eq("user_id", current_user.id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return AnalysisResponse(**result.data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis"
        )

@router.delete("/analyses/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete analysis by ID
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("analyses") \
            .delete() \
            .eq("id", analysis_id) \
            .eq("user_id", current_user.id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        return {"message": "Analysis deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis"
        ) 