import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.core.auth import get_current_user
from app.core.rate_limiter import RateLimiter
from app.services.analytics import AnalyticsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/app.log", rotation="1 day", retention="30 days", level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting GymformAI backend...")
    
    # Initialize database
    await init_db()
    
    # Initialize rate limiter
    app.state.rate_limiter = RateLimiter()
    
    # Initialize analytics service
    app.state.analytics = AnalyticsService()
    
    logger.info("GymformAI backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GymformAI backend...")

# Create FastAPI app
app = FastAPI(
    title="GymformAI API",
    description="AI-powered fitness form analysis API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else settings.ALLOWED_HOSTS,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GymformAI API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None,
    }

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation exceptions"""
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"General Exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware"""
    if hasattr(app.state, 'rate_limiter'):
        client_ip = request.client.host
        if not app.state.rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )
    
    response = await call_next(request)
    return response

# Analytics middleware
@app.middleware("http")
async def analytics_middleware(request, call_next):
    """Analytics middleware"""
    response = await call_next(request)
    
    if hasattr(app.state, 'analytics'):
        # Track API usage
        await app.state.analytics.track_api_usage(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            user_agent=request.headers.get("user-agent"),
        )
    
    return response

# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(current_user=Depends(get_current_user)):
    """Example protected endpoint"""
    return {
        "message": "This is a protected endpoint",
        "user_id": current_user.id,
        "email": current_user.email,
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    ) 