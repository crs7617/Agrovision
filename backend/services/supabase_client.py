"""
Supabase Client Configuration
Provides a singleton Supabase client for database operations
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not found in .env file")
    logger.warning("Database features will not work without SUPABASE_URL and SUPABASE_KEY")
    supabase: Client = None
else:
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"✓ Supabase client initialized: {SUPABASE_URL[:30]}...")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None


def get_supabase_client() -> Client:
    """
    Get the Supabase client instance
    Returns:
        Supabase client or None if not configured
    """
    if supabase is None:
        raise Exception("Supabase client not initialized. Check your .env configuration.")
    return supabase


def check_connection() -> bool:
    """
    Check if Supabase connection is working
    Returns:
        True if connected, False otherwise
    """
    if supabase is None:
        return False
    
    try:
        # Try a simple query to check connection
        result = supabase.table("farms").select("id").limit(1).execute()
        logger.info("✓ Supabase connection verified")
        return True
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False
