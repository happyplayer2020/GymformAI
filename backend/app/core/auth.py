from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from loguru import logger

from app.core.database import get_supabase_client
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    try:
        token = credentials.credentials
        supabase = get_supabase_client()
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user_data = supabase.table("users").select("*").eq("id", user_response.user.id).single().execute()
        
        if not user_data.data:
            # Create user if not exists
            user_data = supabase.table("users").insert({
                "id": user_response.user.id,
                "email": user_response.user.email,
                "subscription_status": "free"
            }).execute()
        
        user = User(**user_data.data)
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    """
    try:
        if not credentials:
            return None
        
        return await get_current_user(credentials)
        
    except HTTPException:
        return None 