from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """User signup endpoint"""
    # This would typically handle user registration
    # For now, we'll return a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Signup handled by Supabase Auth"
    )

@router.post("/signin", response_model=UserResponse)
async def signin(user_data: UserCreate):
    """User signin endpoint"""
    # This would typically handle user login
    # For now, we'll return a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Signin handled by Supabase Auth"
    ) 