import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "GymformAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://your-domain.com"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET: str = "your-jwt-secret-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-supabase-service-role-key"
    
    # OpenAI
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_your-stripe-secret-key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your-stripe-publishable-key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your-stripe-webhook-secret"
    STRIPE_PRICE_ID: str = "price_your-stripe-price-id"
    
    # Analytics
    MIXPANEL_TOKEN: str = "your-mixpanel-token"
    
    # File Upload
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_VIDEO_TYPES: List[str] = ["mp4", "webm", "mov"]
    UPLOAD_DIR: str = "./uploads"
    MAX_VIDEO_DURATION: int = 300  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_DAY: int = 1000
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    # Subscription Limits
    FREE_DAILY_LIMIT: int = 3
    PRO_DAILY_LIMIT: int = 1000
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_VIDEO_TYPES", pre=True)
    def assemble_video_types(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True) 