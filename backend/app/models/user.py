from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    subscription_status: str = "free"
    subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """User update model"""
    subscription_status: Optional[str] = None
    subscription_id: Optional[str] = None

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: EmailStr
    subscription_status: str
    created_at: datetime 