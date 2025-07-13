from datetime import datetime, timedelta
from typing import Dict, Any
from loguru import logger

from app.core.database import get_supabase_client

class UsageTracker:
    """Track user usage and enforce limits"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_daily_usage(self, user_id: str) -> int:
        """Get user's daily analysis count"""
        try:
            today = datetime.utcnow().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            result = self.supabase.table("analyses") \
                .select("id", count="exact") \
                .eq("user_id", user_id) \
                .gte("created_at", start_of_day.isoformat()) \
                .lte("created_at", end_of_day.isoformat()) \
                .execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Error getting daily usage for user {user_id}: {str(e)}")
            return 0
    
    async def increment_daily_usage(self, user_id: str):
        """Increment daily usage count"""
        try:
            # This is handled by the analysis creation, but we can add additional tracking here
            logger.info(f"Incremented daily usage for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error incrementing daily usage for user {user_id}: {str(e)}")
    
    async def get_user_limits(self, user_id: str) -> Dict[str, Any]:
        """Get user's current limits and usage"""
        try:
            # Get user subscription status
            user_result = self.supabase.table("users") \
                .select("subscription_status") \
                .eq("id", user_id) \
                .single() \
                .execute()
            
            subscription_status = user_result.data.get("subscription_status", "free")
            
            # Get daily usage
            daily_usage = await self.get_daily_usage(user_id)
            
            # Determine limits based on subscription
            if subscription_status == "pro":
                daily_limit = 1000  # High limit for pro users
            else:
                daily_limit = 3  # Free user limit
            
            return {
                "subscription_status": subscription_status,
                "daily_usage": daily_usage,
                "daily_limit": daily_limit,
                "remaining": max(0, daily_limit - daily_usage)
            }
            
        except Exception as e:
            logger.error(f"Error getting user limits for user {user_id}: {str(e)}")
            return {
                "subscription_status": "free",
                "daily_usage": 0,
                "daily_limit": 3,
                "remaining": 3
            }
    
    async def can_analyze(self, user_id: str) -> bool:
        """Check if user can perform analysis"""
        try:
            limits = await self.get_user_limits(user_id)
            return limits["remaining"] > 0
            
        except Exception as e:
            logger.error(f"Error checking analysis permission for user {user_id}: {str(e)}")
            return False 