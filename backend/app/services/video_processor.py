import cv2
import numpy as np
from typing import List, Optional
from loguru import logger

class VideoProcessor:
    """Video processing service for extracting frames and metadata"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    async def extract_frames(
        self,
        video_path: str,
        max_frames: int = 100,
        sample_rate: int = 5
    ) -> List[np.ndarray]:
        """
        Extract frames from video file
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract
            sample_rate: Extract every Nth frame
            
        Returns:
            List of frame arrays
        """
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return []
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video properties: {total_frames} frames, {fps} FPS, {duration:.2f}s duration")
            
            frames = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Extract every Nth frame
                if frame_count % sample_rate == 0:
                    # Resize frame for processing (maintain aspect ratio)
                    frame = self._resize_frame(frame, max_width=640)
                    frames.append(frame)
                    extracted_count += 1
                    
                    # Stop if we have enough frames
                    if extracted_count >= max_frames:
                        break
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"Extracted {len(frames)} frames from video")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
    
    def _resize_frame(self, frame: np.ndarray, max_width: int = 640) -> np.ndarray:
        """Resize frame while maintaining aspect ratio"""
        try:
            height, width = frame.shape[:2]
            
            if width <= max_width:
                return frame
            
            # Calculate new dimensions
            ratio = max_width / width
            new_width = max_width
            new_height = int(height * ratio)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            return resized_frame
            
        except Exception as e:
            logger.error(f"Error resizing frame: {str(e)}")
            return frame
    
    async def get_video_metadata(self, video_path: str) -> dict:
        """Get video metadata"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {}
            
            metadata = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            }
            
            cap.release()
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting video metadata: {str(e)}")
            return {}
    
    async def create_thumbnail(self, video_path: str, output_path: str) -> bool:
        """Create a thumbnail from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return False
            
            # Get middle frame
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame = total_frames // 2
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            
            if not ret:
                cap.release()
                return False
            
            # Resize thumbnail
            frame = self._resize_frame(frame, max_width=320)
            
            # Save thumbnail
            cv2.imwrite(output_path, frame)
            cap.release()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return False
    
    def validate_video_format(self, file_path: str) -> bool:
        """Validate video file format"""
        try:
            import os
            file_extension = os.path.splitext(file_path)[1].lower()
            return file_extension in self.supported_formats
        except Exception as e:
            logger.error(f"Error validating video format: {str(e)}")
            return False 