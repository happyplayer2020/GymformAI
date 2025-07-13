import numpy as np
from typing import List, Dict, Any, Tuple
from loguru import logger

class RepCounter:
    """Repetition counting service using pose analysis"""
    
    def __init__(self):
        # Exercise type detection thresholds
        self.exercise_patterns = {
            'squat': {
                'knee_angle_range': (60, 160),
                'hip_movement_threshold': 0.1,
                'key_joints': ['left_knee', 'right_knee', 'left_hip', 'right_hip']
            },
            'push_up': {
                'elbow_angle_range': (60, 160),
                'shoulder_movement_threshold': 0.05,
                'key_joints': ['left_elbow', 'right_elbow', 'left_shoulder', 'right_shoulder']
            },
            'plank': {
                'spine_angle_threshold': 10,
                'min_duration': 2.0,  # seconds
                'key_joints': ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
            },
            'deadlift': {
                'hip_movement_threshold': 0.15,
                'knee_angle_range': (80, 170),
                'key_joints': ['left_hip', 'right_hip', 'left_knee', 'right_knee']
            }
        }
    
    async def count_reps(
        self,
        keypoints_data: List[Dict[str, Any]]
    ) -> Tuple[int, str]:
        """
        Count repetitions and detect exercise type
        
        Args:
            keypoints_data: List of pose keypoints for each frame
            
        Returns:
            Tuple of (rep_count, exercise_type)
        """
        try:
            if not keypoints_data:
                return 0, "unknown"
            
            # Detect exercise type
            exercise_type = self._detect_exercise_type(keypoints_data)
            
            # Count repetitions based on exercise type
            rep_count = self._count_repetitions(keypoints_data, exercise_type)
            
            logger.info(f"Detected {exercise_type} with {rep_count} repetitions")
            return rep_count, exercise_type
            
        except Exception as e:
            logger.error(f"Error counting reps: {str(e)}")
            return 0, "unknown"
    
    def _detect_exercise_type(self, keypoints_data: List[Dict[str, Any]]) -> str:
        """Detect exercise type based on pose patterns"""
        try:
            scores = {}
            
            for exercise, pattern in self.exercise_patterns.items():
                score = self._calculate_exercise_score(keypoints_data, pattern)
                scores[exercise] = score
            
            # Return exercise with highest score
            best_exercise = max(scores, key=scores.get)
            
            # Only return if score is above threshold
            if scores[best_exercise] > 0.6:
                return best_exercise
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting exercise type: {str(e)}")
            return "unknown"
    
    def _calculate_exercise_score(
        self,
        keypoints_data: List[Dict[str, Any]],
        pattern: Dict[str, Any]
    ) -> float:
        """Calculate how well the pose sequence matches an exercise pattern"""
        try:
            score = 0.0
            total_frames = len(keypoints_data)
            
            if total_frames == 0:
                return 0.0
            
            # Check key joints visibility
            visible_frames = 0
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                metrics = keypoints.get('metrics', {})
                
                # Check if key joints are visible
                key_joints_visible = all(
                    joint in keypoints and keypoints[joint].get('visibility', 0) > 0.5
                    for joint in pattern['key_joints']
                )
                
                if key_joints_visible:
                    visible_frames += 1
            
            visibility_score = visible_frames / total_frames
            score += visibility_score * 0.3
            
            # Exercise-specific scoring
            if 'knee_angle_range' in pattern:
                knee_score = self._check_knee_angles(keypoints_data, pattern['knee_angle_range'])
                score += knee_score * 0.3
            
            if 'elbow_angle_range' in pattern:
                elbow_score = self._check_elbow_angles(keypoints_data, pattern['elbow_angle_range'])
                score += elbow_score * 0.3
            
            if 'hip_movement_threshold' in pattern:
                hip_score = self._check_hip_movement(keypoints_data, pattern['hip_movement_threshold'])
                score += hip_score * 0.2
            
            if 'shoulder_movement_threshold' in pattern:
                shoulder_score = self._check_shoulder_movement(keypoints_data, pattern['shoulder_movement_threshold'])
                score += shoulder_score * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating exercise score: {str(e)}")
            return 0.0
    
    def _check_knee_angles(
        self,
        keypoints_data: List[Dict[str, Any]],
        angle_range: Tuple[float, float]
    ) -> float:
        """Check if knee angles are within expected range"""
        try:
            valid_frames = 0
            total_frames = len(keypoints_data)
            
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                metrics = keypoints.get('metrics', {})
                
                left_knee_angle = metrics.get('left_knee_angle', 0)
                right_knee_angle = metrics.get('right_knee_angle', 0)
                
                # Check if angles are within range
                if (angle_range[0] <= left_knee_angle <= angle_range[1] and
                    angle_range[0] <= right_knee_angle <= angle_range[1]):
                    valid_frames += 1
            
            return valid_frames / total_frames if total_frames > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error checking knee angles: {str(e)}")
            return 0.0
    
    def _check_elbow_angles(
        self,
        keypoints_data: List[Dict[str, Any]],
        angle_range: Tuple[float, float]
    ) -> float:
        """Check if elbow angles are within expected range"""
        try:
            valid_frames = 0
            total_frames = len(keypoints_data)
            
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                metrics = keypoints.get('metrics', {})
                
                left_elbow_angle = metrics.get('left_elbow_angle', 0)
                right_elbow_angle = metrics.get('right_elbow_angle', 0)
                
                # Check if angles are within range
                if (angle_range[0] <= left_elbow_angle <= angle_range[1] and
                    angle_range[0] <= right_elbow_angle <= angle_range[1]):
                    valid_frames += 1
            
            return valid_frames / total_frames if total_frames > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error checking elbow angles: {str(e)}")
            return 0.0
    
    def _check_hip_movement(
        self,
        keypoints_data: List[Dict[str, Any]],
        threshold: float
    ) -> float:
        """Check if there's significant hip movement"""
        try:
            if len(keypoints_data) < 2:
                return 0.0
            
            hip_positions = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                
                left_hip = keypoints.get('left_hip', {})
                right_hip = keypoints.get('right_hip', {})
                
                if left_hip and right_hip:
                    hip_center_y = (left_hip.get('y', 0) + right_hip.get('y', 0)) / 2
                    hip_positions.append(hip_center_y)
            
            if len(hip_positions) < 2:
                return 0.0
            
            # Calculate movement range
            movement_range = max(hip_positions) - min(hip_positions)
            
            return min(movement_range / threshold, 1.0)
            
        except Exception as e:
            logger.error(f"Error checking hip movement: {str(e)}")
            return 0.0
    
    def _check_shoulder_movement(
        self,
        keypoints_data: List[Dict[str, Any]],
        threshold: float
    ) -> float:
        """Check if there's significant shoulder movement"""
        try:
            if len(keypoints_data) < 2:
                return 0.0
            
            shoulder_positions = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                
                left_shoulder = keypoints.get('left_shoulder', {})
                right_shoulder = keypoints.get('right_shoulder', {})
                
                if left_shoulder and right_shoulder:
                    shoulder_center_y = (left_shoulder.get('y', 0) + right_shoulder.get('y', 0)) / 2
                    shoulder_positions.append(shoulder_center_y)
            
            if len(shoulder_positions) < 2:
                return 0.0
            
            # Calculate movement range
            movement_range = max(shoulder_positions) - min(shoulder_positions)
            
            return min(movement_range / threshold, 1.0)
            
        except Exception as e:
            logger.error(f"Error checking shoulder movement: {str(e)}")
            return 0.0
    
    def _count_repetitions(
        self,
        keypoints_data: List[Dict[str, Any]],
        exercise_type: str
    ) -> int:
        """Count repetitions based on exercise type"""
        try:
            if exercise_type == "squat":
                return self._count_squat_reps(keypoints_data)
            elif exercise_type == "push_up":
                return self._count_pushup_reps(keypoints_data)
            elif exercise_type == "plank":
                return self._count_plank_duration(keypoints_data)
            elif exercise_type == "deadlift":
                return self._count_deadlift_reps(keypoints_data)
            else:
                return self._count_generic_reps(keypoints_data)
                
        except Exception as e:
            logger.error(f"Error counting repetitions: {str(e)}")
            return 0
    
    def _count_squat_reps(self, keypoints_data: List[Dict[str, Any]]) -> int:
        """Count squat repetitions using knee angles"""
        try:
            if len(keypoints_data) < 10:
                return 0
            
            knee_angles = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                metrics = keypoints.get('metrics', {})
                
                left_knee = metrics.get('left_knee_angle', 0)
                right_knee = metrics.get('right_knee_angle', 0)
                
                if left_knee > 0 and right_knee > 0:
                    knee_angles.append((left_knee + right_knee) / 2)
            
            if len(knee_angles) < 5:
                return 0
            
            # Count peaks (squat down positions)
            peaks = self._find_peaks(knee_angles, threshold=120)
            return len(peaks)
            
        except Exception as e:
            logger.error(f"Error counting squat reps: {str(e)}")
            return 0
    
    def _count_pushup_reps(self, keypoints_data: List[Dict[str, Any]]) -> int:
        """Count push-up repetitions using elbow angles"""
        try:
            if len(keypoints_data) < 10:
                return 0
            
            elbow_angles = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                metrics = keypoints.get('metrics', {})
                
                left_elbow = metrics.get('left_elbow_angle', 0)
                right_elbow = metrics.get('right_elbow_angle', 0)
                
                if left_elbow > 0 and right_elbow > 0:
                    elbow_angles.append((left_elbow + right_elbow) / 2)
            
            if len(elbow_angles) < 5:
                return 0
            
            # Count peaks (down positions)
            peaks = self._find_peaks(elbow_angles, threshold=90)
            return len(peaks)
            
        except Exception as e:
            logger.error(f"Error counting pushup reps: {str(e)}")
            return 0
    
    def _count_plank_duration(self, keypoints_data: List[Dict[str, Any]]) -> int:
        """Count plank duration in seconds"""
        try:
            # Assume 30 FPS for duration calculation
            fps = 30
            duration_seconds = len(keypoints_data) / fps
            
            # Return duration in seconds (rounded)
            return max(1, int(duration_seconds))
            
        except Exception as e:
            logger.error(f"Error counting plank duration: {str(e)}")
            return 0
    
    def _count_deadlift_reps(self, keypoints_data: List[Dict[str, Any]]) -> int:
        """Count deadlift repetitions using hip movement"""
        try:
            if len(keypoints_data) < 10:
                return 0
            
            hip_positions = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                
                left_hip = keypoints.get('left_hip', {})
                right_hip = keypoints.get('right_hip', {})
                
                if left_hip and right_hip:
                    hip_center_y = (left_hip.get('y', 0) + right_hip.get('y', 0)) / 2
                    hip_positions.append(hip_center_y)
            
            if len(hip_positions) < 5:
                return 0
            
            # Count peaks (up positions)
            peaks = self._find_peaks(hip_positions, threshold=0.5, reverse=True)
            return len(peaks)
            
        except Exception as e:
            logger.error(f"Error counting deadlift reps: {str(e)}")
            return 0
    
    def _count_generic_reps(self, keypoints_data: List[Dict[str, Any]]) -> int:
        """Generic repetition counting using overall movement"""
        try:
            if len(keypoints_data) < 10:
                return 0
            
            # Use hip movement as a general indicator
            hip_positions = []
            for frame_data in keypoints_data:
                keypoints = frame_data.get('keypoints', {})
                
                left_hip = keypoints.get('left_hip', {})
                right_hip = keypoints.get('right_hip', {})
                
                if left_hip and right_hip:
                    hip_center_y = (left_hip.get('y', 0) + right_hip.get('y', 0)) / 2
                    hip_positions.append(hip_center_y)
            
            if len(hip_positions) < 5:
                return 0
            
            # Count significant movements
            peaks = self._find_peaks(hip_positions, threshold=0.1)
            return len(peaks)
            
        except Exception as e:
            logger.error(f"Error counting generic reps: {str(e)}")
            return 0
    
    def _find_peaks(
        self,
        data: List[float],
        threshold: float,
        reverse: bool = False
    ) -> List[int]:
        """Find peaks in data above threshold"""
        try:
            peaks = []
            data_array = np.array(data)
            
            if reverse:
                # Find valleys (minima)
                for i in range(1, len(data_array) - 1):
                    if (data_array[i] < data_array[i-1] and 
                        data_array[i] < data_array[i+1] and 
                        data_array[i] < threshold):
                        peaks.append(i)
            else:
                # Find peaks (maxima)
                for i in range(1, len(data_array) - 1):
                    if (data_array[i] > data_array[i-1] and 
                        data_array[i] > data_array[i+1] and 
                        data_array[i] > threshold):
                        peaks.append(i)
            
            return peaks
            
        except Exception as e:
            logger.error(f"Error finding peaks: {str(e)}")
            return [] 