from fastapi import APIRouter

from app.api.v1.endpoints import analyze, auth, users, subscriptions

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"]) 