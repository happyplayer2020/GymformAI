from supabase import create_client, Client
from app.core.config import settings
from loguru import logger

# Global Supabase client
_supabase_client: Client = None

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    
    return _supabase_client

async def init_db():
    """Initialize database connection"""
    try:
        client = get_supabase_client()
        
        # Test connection
        result = client.table("users").select("count", count="exact").limit(1).execute()
        
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

async def close_db():
    """Close database connection"""
    global _supabase_client
    
    if _supabase_client:
        _supabase_client = None
        logger.info("Database connection closed") 