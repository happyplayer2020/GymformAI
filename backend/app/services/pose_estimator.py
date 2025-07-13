import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any, Optional, List
from loguru import logger

class PoseEstimator:
    """Pose estimation service using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # 0, 1, or 2 (higher = more accurate but slower)
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define key landmarks we're interested in
        self.key_landmarks = {
            'nose': self.mp_pose.PoseLandmark.NOSE,
            'left_eye': self.mp_pose.PoseLandmark.LEFT_EYE,
            'right_eye': self.mp_pose.PoseLandmark.RIGHT_EYE,
            'left_ear': self.mp_pose.PoseLandmark.LEFT_EAR,
            'right_ear': self.mp_pose.PoseLandmark.RIGHT_EAR,
            'left_shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
            'left_hip': self.mp_pose.PoseLandmark.LEFT_HIP,
            'right_hip': self.mp_pose.PoseLandmark.RIGHT_HIP,
            'left_knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
            'right_knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE,
            'left_heel': self.mp_pose.PoseLandmark.LEFT_HEEL,
            'right_heel': self.mp_pose.PoseLandmark.RIGHT_HEEL,
            'left_foot_index': self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            'right_foot_index': self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
        }
    
    async def extract_pose(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Extract pose keypoints from a single frame
        
        Args:
            frame: Input image frame as numpy array
            
        Returns:
            Dictionary with keypoint coordinates and confidence scores
        """
        try:
            # Convert BGR to RGB (MediaPipe expects RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.pose.process(rgb_frame)
            
            if not results.pose_landmarks:
                return None
            
            # Extract keypoints
            keypoints = {}
            landmarks = results.pose_landmarks.landmark
            
            for name, landmark_id in self.key_landmarks.items():
                landmark = landmarks[landmark_id]
                
                keypoints[name] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility,
                    'confidence': landmark.visibility  # MediaPipe uses visibility as confidence
                }
            
            # Calculate additional metrics
            keypoints['metrics'] = self._calculate_pose_metrics(keypoints)
            
            return keypoints
            
        except Exception as e:
            logger.error(f"Error extracting pose: {str(e)}")
            return None
    
    def _calculate_pose_metrics(self, keypoints: Dict[str, Any]) -> Dict[str, float]:
        """Calculate additional pose metrics"""
        metrics = {}
        
        try:
            # Calculate shoulder width
            if 'left_shoulder' in keypoints and 'right_shoulder' in keypoints:
                left_shoulder = keypoints['left_shoulder']
                right_shoulder = keypoints['right_shoulder']
                
                shoulder_width = np.sqrt(
                    (left_shoulder['x'] - right_shoulder['x'])**2 +
                    (left_shoulder['y'] - right_shoulder['y'])**2
                )
                metrics['shoulder_width'] = shoulder_width
            
            # Calculate hip width
            if 'left_hip' in keypoints and 'right_hip' in keypoints:
                left_hip = keypoints['left_hip']
                right_hip = keypoints['right_hip']
                
                hip_width = np.sqrt(
                    (left_hip['x'] - right_hip['x'])**2 +
                    (left_hip['y'] - right_hip['y'])**2
                )
                metrics['hip_width'] = hip_width
            
            # Calculate spine angle (shoulder to hip)
            if all(k in keypoints for k in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
                shoulder_center_x = (keypoints['left_shoulder']['x'] + keypoints['right_shoulder']['x']) / 2
                shoulder_center_y = (keypoints['left_shoulder']['y'] + keypoints['right_shoulder']['y']) / 2
                hip_center_x = (keypoints['left_hip']['x'] + keypoints['right_hip']['x']) / 2
                hip_center_y = (keypoints['left_hip']['y'] + keypoints['right_hip']['y']) / 2
                
                spine_angle = np.arctan2(
                    shoulder_center_x - hip_center_x,
                    shoulder_center_y - hip_center_y
                ) * 180 / np.pi
                metrics['spine_angle'] = spine_angle
            
            # Calculate knee angles
            if all(k in keypoints for k in ['left_hip', 'left_knee', 'left_ankle']):
                left_knee_angle = self._calculate_angle(
                    keypoints['left_hip'],
                    keypoints['left_knee'],
                    keypoints['left_ankle']
                )
                metrics['left_knee_angle'] = left_knee_angle
            
            if all(k in keypoints for k in ['right_hip', 'right_knee', 'right_ankle']):
                right_knee_angle = self._calculate_angle(
                    keypoints['right_hip'],
                    keypoints['right_knee'],
                    keypoints['right_ankle']
                )
                metrics['right_knee_angle'] = right_knee_angle
            
            # Calculate elbow angles
            if all(k in keypoints for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
                left_elbow_angle = self._calculate_angle(
                    keypoints['left_shoulder'],
                    keypoints['left_elbow'],
                    keypoints['left_wrist']
                )
                metrics['left_elbow_angle'] = left_elbow_angle
            
            if all(k in keypoints for k in ['right_shoulder', 'right_elbow', 'right_wrist']):
                right_elbow_angle = self._calculate_angle(
                    keypoints['right_shoulder'],
                    keypoints['right_elbow'],
                    keypoints['right_wrist']
                )
                metrics['right_elbow_angle'] = right_elbow_angle
            
            # Calculate overall pose confidence
            visibilities = [kp['visibility'] for kp in keypoints.values() if isinstance(kp, dict) and 'visibility' in kp]
            if visibilities:
                metrics['overall_confidence'] = np.mean(visibilities)
            
        except Exception as e:
            logger.error(f"Error calculating pose metrics: {str(e)}")
        
        return metrics
    
    def _calculate_angle(self, point1: Dict[str, float], point2: Dict[str, float], point3: Dict[str, float]) -> float:
        """Calculate angle between three points"""
        try:
            # Vector 1: point2 to point1
            v1_x = point1['x'] - point2['x']
            v1_y = point1['y'] - point2['y']
            
            # Vector 2: point2 to point3
            v2_x = point3['x'] - point2['x']
            v2_y = point3['y'] - point2['y']
            
            # Calculate dot product
            dot_product = v1_x * v2_x + v1_y * v2_y
            
            # Calculate magnitudes
            mag1 = np.sqrt(v1_x**2 + v1_y**2)
            mag2 = np.sqrt(v2_x**2 + v2_y**2)
            
            # Calculate angle
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot_product / (mag1 * mag2)
                cos_angle = np.clip(cos_angle, -1, 1)  # Clamp to valid range
                angle = np.arccos(cos_angle) * 180 / np.pi
                return angle
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating angle: {str(e)}")
            return 0.0
    
    async def extract_pose_sequence(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """
        Extract pose keypoints from a sequence of frames
        
        Args:
            frames: List of input image frames
            
        Returns:
            List of pose keypoints for each frame
        """
        pose_sequence = []
        
        for i, frame in enumerate(frames):
            keypoints = await self.extract_pose(frame)
            if keypoints:
                pose_sequence.append({
                    'frame': i,
                    'keypoints': keypoints,
                    'timestamp': i / len(frames)  # Approximate timestamp
                })
        
        return pose_sequence
    
    def get_pose_landmarks(self) -> Dict[str, int]:
        """Get mapping of landmark names to indices"""
        return self.key_landmarks.copy()
    
    def __del__(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close() 