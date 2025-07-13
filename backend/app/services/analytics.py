import asyncio
from typing import Dict, Any, Optional
import mixpanel
from loguru import logger

from app.core.config import settings

class AnalyticsService:
    """Analytics service using Mixpanel"""
    
    def __init__(self):
        self.mixpanel = mixpanel.Mixpanel(settings.MIXPANEL_TOKEN) if settings.MIXPANEL_TOKEN else None
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Track an event"""
        try:
            if not self.mixpanel:
                return
            
            # Prepare properties
            event_properties = properties or {}
            if user_id:
                event_properties['user_id'] = user_id
            
            # Track event
            self.mixpanel.track(user_id or 'anonymous', event_name, event_properties)
            
            logger.info(f"Tracked event: {event_name} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking event {event_name}: {str(e)}")
    
    async def track_api_usage(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        user_agent: Optional[str] = None
    ):
        """Track API usage"""
        try:
            properties = {
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'user_agent': user_agent or 'unknown'
            }
            
            await self.track_event('api_request', properties=properties)
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {str(e)}")
    
    async def identify_user(
        self,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Identify a user"""
        try:
            if not self.mixpanel:
                return
            
            user_properties = properties or {}
            self.mixpanel.people_set(user_id, user_properties)
            
            logger.info(f"Identified user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error identifying user {user_id}: {str(e)}")
    
    async def track_user_registration(
        self,
        user_id: str,
        email: str,
        signup_method: str = 'email'
    ):
        """Track user registration"""
        try:
            properties = {
                'email': email,
                'signup_method': signup_method,
                'user_type': 'new'
            }
            
            await self.track_event('user_registered', user_id, properties)
            await self.identify_user(user_id, {
                'email': email,
                'signup_method': signup_method,
                'subscription_status': 'free',
                'total_analyses': 0
            })
            
        except Exception as e:
            logger.error(f"Error tracking user registration: {str(e)}")
    
    async def track_user_login(
        self,
        user_id: str,
        login_method: str = 'email'
    ):
        """Track user login"""
        try:
            properties = {
                'login_method': login_method
            }
            
            await self.track_event('user_logged_in', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking user login: {str(e)}")
    
    async def track_video_upload(
        self,
        user_id: str,
        file_size: int,
        file_type: str,
        duration: Optional[float] = None
    ):
        """Track video upload"""
        try:
            properties = {
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'file_type': file_type,
                'duration_seconds': duration
            }
            
            await self.track_event('video_uploaded', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking video upload: {str(e)}")
    
    async def track_analysis_started(
        self,
        user_id: str,
        exercise_type: Optional[str] = None
    ):
        """Track analysis started"""
        try:
            properties = {
                'exercise_type': exercise_type or 'auto_detected'
            }
            
            await self.track_event('analysis_started', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking analysis started: {str(e)}")
    
    async def track_analysis_completed(
        self,
        user_id: str,
        exercise_type: str,
        score: float,
        rep_count: int,
        processing_time: float,
        risks_detected: int = 0
    ):
        """Track analysis completion"""
        try:
            properties = {
                'exercise_type': exercise_type,
                'score': score,
                'rep_count': rep_count,
                'processing_time_seconds': round(processing_time, 2),
                'risks_detected': risks_detected,
                'score_category': self._get_score_category(score)
            }
            
            await self.track_event('analysis_completed', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking analysis completion: {str(e)}")
    
    async def track_analysis_failed(
        self,
        user_id: str,
        error_type: str,
        error_message: str
    ):
        """Track analysis failure"""
        try:
            properties = {
                'error_type': error_type,
                'error_message': error_message
            }
            
            await self.track_event('analysis_failed', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking analysis failure: {str(e)}")
    
    async def track_subscription_upgrade(
        self,
        user_id: str,
        plan: str,
        amount: float,
        billing_cycle: str
    ):
        """Track subscription upgrade"""
        try:
            properties = {
                'plan': plan,
                'amount': amount,
                'billing_cycle': billing_cycle,
                'currency': 'EUR'
            }
            
            await self.track_event('subscription_upgraded', user_id, properties)
            await self.identify_user(user_id, {
                'subscription_status': 'pro',
                'plan': plan,
                'billing_cycle': billing_cycle
            })
            
        except Exception as e:
            logger.error(f"Error tracking subscription upgrade: {str(e)}")
    
    async def track_subscription_cancelled(
        self,
        user_id: str,
        plan: str,
        reason: Optional[str] = None
    ):
        """Track subscription cancellation"""
        try:
            properties = {
                'plan': plan,
                'cancellation_reason': reason or 'unknown'
            }
            
            await self.track_event('subscription_cancelled', user_id, properties)
            await self.identify_user(user_id, {
                'subscription_status': 'cancelled'
            })
            
        except Exception as e:
            logger.error(f"Error tracking subscription cancellation: {str(e)}")
    
    async def track_feature_usage(
        self,
        user_id: str,
        feature_name: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Track feature usage"""
        try:
            event_properties = properties or {}
            event_properties['feature'] = feature_name
            
            await self.track_event('feature_used', user_id, event_properties)
            
        except Exception as e:
            logger.error(f"Error tracking feature usage: {str(e)}")
    
    async def track_user_engagement(
        self,
        user_id: str,
        session_duration: float,
        pages_visited: int,
        actions_performed: int
    ):
        """Track user engagement metrics"""
        try:
            properties = {
                'session_duration_minutes': round(session_duration / 60, 2),
                'pages_visited': pages_visited,
                'actions_performed': actions_performed
            }
            
            await self.track_event('session_ended', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking user engagement: {str(e)}")
    
    async def track_error(
        self,
        user_id: Optional[str],
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Track application errors"""
        try:
            properties = {
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {}
            }
            
            await self.track_event('application_error', user_id, properties)
            
        except Exception as e:
            logger.error(f"Error tracking application error: {str(e)}")
    
    def _get_score_category(self, score: float) -> str:
        """Get score category for analytics"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= 70:
            return 'fair'
        elif score >= 60:
            return 'poor'
        else:
            return 'very_poor' 