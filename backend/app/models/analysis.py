from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class AnalysisCreate(BaseModel):
    """Analysis creation model"""
    user_id: str
    video_filename: str
    exercise_type: str
    form_score: float
    rep_count: int
    risks: List[str]
    corrections: List[str]
    keypoints_data: List[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    id: str
    user_id: str
    video_filename: str
    exercise_type: str
    form_score: float
    rep_count: int
    risks: List[str]
    corrections: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisUpdate(BaseModel):
    """Analysis update model"""
    exercise_type: Optional[str] = None
    form_score: Optional[float] = None
    rep_count: Optional[int] = None
    risks: Optional[List[str]] = None
    corrections: Optional[List[str]] = None 