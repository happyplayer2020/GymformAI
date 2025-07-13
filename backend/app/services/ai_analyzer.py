import json
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings

class AIAnalyzer:
    """AI service for analyzing workout form using OpenAI GPT-4"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def analyze_form(
        self,
        keypoints_data: List[Dict[str, Any]],
        exercise_type: str,
        rep_count: int
    ) -> Dict[str, Any]:
        """
        Analyze workout form using AI
        
        Args:
            keypoints_data: List of pose keypoints for each frame
            exercise_type: Detected exercise type
            rep_count: Number of repetitions detected
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Prepare keypoints data for AI
            keypoints_summary = self._prepare_keypoints_summary(keypoints_data)
            
            # Create AI prompt
            prompt = self._create_analysis_prompt(
                keypoints_summary=keypoints_summary,
                exercise_type=exercise_type,
                rep_count=rep_count
            )
            
            # Get AI analysis
            response = await self._get_ai_analysis(prompt)
            
            # Parse and validate response
            analysis = self._parse_ai_response(response)
            
            logger.info(f"AI analysis completed for {exercise_type} with score {analysis['score']}")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            # Return fallback analysis
            return self._get_fallback_analysis(exercise_type, rep_count)
    
    def _prepare_keypoints_summary(self, keypoints_data: List[Dict[str, Any]]) -> str:
        """Prepare keypoints data for AI analysis"""
        try:
            # Sample frames to reduce data size (every 5th frame)
            sampled_data = keypoints_data[::5]
            
            # Extract key joint positions
            summary = []
            for frame_data in sampled_data[:20]:  # Limit to 20 frames
                frame_num = frame_data["frame"]
                keypoints = frame_data["keypoints"]
                
                # Extract key joints (shoulders, elbows, wrists, hips, knees, ankles)
                key_joints = {
                    "left_shoulder": keypoints.get("left_shoulder", {}),
                    "right_shoulder": keypoints.get("right_shoulder", {}),
                    "left_elbow": keypoints.get("left_elbow", {}),
                    "right_elbow": keypoints.get("right_elbow", {}),
                    "left_wrist": keypoints.get("left_wrist", {}),
                    "right_wrist": keypoints.get("right_wrist", {}),
                    "left_hip": keypoints.get("left_hip", {}),
                    "right_hip": keypoints.get("right_hip", {}),
                    "left_knee": keypoints.get("left_knee", {}),
                    "right_knee": keypoints.get("right_knee", {}),
                    "left_ankle": keypoints.get("left_ankle", {}),
                    "right_ankle": keypoints.get("right_ankle", {}),
                }
                
                summary.append({
                    "frame": frame_num,
                    "joints": key_joints
                })
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error preparing keypoints summary: {str(e)}")
            return "[]"
    
    def _create_analysis_prompt(
        self,
        keypoints_summary: str,
        exercise_type: str,
        rep_count: int
    ) -> str:
        """Create the AI analysis prompt"""
        
        system_prompt = """You are GymformAI, an expert fitness coach analyzing workout videos. You have extensive knowledge of exercise form, biomechanics, and common form issues.

Your task is to analyze the provided pose keypoints data and provide:
1. A form score from 1-10 (where 10 is perfect form)
2. 2 main posture/form issues detected
3. 1 specific correction for each issue
4. Validate the detected exercise type and rep count

Be specific, actionable, and professional in your feedback. Focus on the most critical form issues that could lead to injury or reduce exercise effectiveness."""

        user_prompt = f"""Here are the detected body keypoints for frames (JSON):
{keypoints_summary}

The exercise is: {exercise_type}
The detected number of reps is: {rep_count}

Please analyze this data and provide:
- Diagnose 2 main posture/form issues
- Give 1 specific correction per issue
- Score the form (1–10)
- Validate if the exercise type and rep count seem accurate

Output your response as JSON in this exact format:
{{
  "exercise": "{exercise_type}",
  "score": 7.5,
  "risks": ["Issue 1 description", "Issue 2 description"],
  "corrections": ["Correction 1", "Correction 2"],
  "rep_count": {rep_count},
  "validation": {{
    "exercise_type_accurate": true,
    "rep_count_accurate": true,
    "confidence": 0.85
  }}
}}"""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    async def _get_ai_analysis(self, prompt: Dict[str, str]) -> str:
        """Get analysis from OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=1000,
                timeout=30
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["exercise", "score", "risks", "corrections", "rep_count"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate score range
            score = float(data["score"])
            if not (1 <= score <= 10):
                data["score"] = max(1, min(10, score))
            
            # Ensure risks and corrections are lists
            if not isinstance(data["risks"], list):
                data["risks"] = [str(data["risks"])]
            if not isinstance(data["corrections"], list):
                data["corrections"] = [str(data["corrections"])]
            
            # Limit to 2 risks and corrections
            data["risks"] = data["risks"][:2]
            data["corrections"] = data["corrections"][:2]
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def _get_fallback_analysis(self, exercise_type: str, rep_count: int) -> Dict[str, Any]:
        """Provide fallback analysis when AI fails"""
        logger.warning("Using fallback analysis due to AI failure")
        
        return {
            "exercise": exercise_type,
            "score": 6.0,
            "risks": [
                "Unable to analyze form due to technical issues",
                "Please ensure good lighting and clear video for better analysis"
            ],
            "corrections": [
                "Record video in well-lit environment",
                "Ensure full body is visible in frame"
            ],
            "rep_count": rep_count,
            "validation": {
                "exercise_type_accurate": True,
                "rep_count_accurate": True,
                "confidence": 0.5
            }
        }
    
    async def get_exercise_suggestions(self, current_exercise: str) -> List[str]:
        """Get exercise suggestions based on current exercise"""
        try:
            prompt = f"""Based on the exercise "{current_exercise}", suggest 3 related exercises that would complement this workout. 
            Return as a JSON array of exercise names."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fitness expert providing exercise suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            suggestions_text = response.choices[0].message.content
            # Extract JSON array
            start_idx = suggestions_text.find('[')
            end_idx = suggestions_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                suggestions = json.loads(suggestions_text[start_idx:end_idx])
                return suggestions[:3]  # Limit to 3 suggestions
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting exercise suggestions: {str(e)}")
            return [] 