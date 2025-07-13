from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models.user import User, UserResponse
from app.services.usage_tracker import UsageTracker

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        subscription_status=current_user.subscription_status,
        created_at=current_user.created_at
    )

@router.get("/usage")
async def get_user_usage(current_user: User = Depends(get_current_user)):
    """Get user usage information"""
    usage_tracker = UsageTracker()
    limits = await usage_tracker.get_user_limits(current_user.id)
    
    return {
        "user_id": current_user.id,
        "subscription_status": limits["subscription_status"],
        "daily_usage": limits["daily_usage"],
        "daily_limit": limits["daily_limit"],
        "remaining": limits["remaining"]
    } 