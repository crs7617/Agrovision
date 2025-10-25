"""
Farm Management Router
CRUD operations for farms with Supabase integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()


# =====================================================
# Pydantic Models
# =====================================================

class FarmCreate(BaseModel):
    """Model for creating a new farm"""
    name: str = Field(..., min_length=1, max_length=255)
    crop_type: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    area: Optional[float] = Field(None, gt=0)
    location_address: Optional[str] = None
    user_id: str = Field(default="00000000-0000-0000-0000-000000000001")  # Default test user


class FarmUpdate(BaseModel):
    """Model for updating farm"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    crop_type: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    area: Optional[float] = Field(None, gt=0)
    location_address: Optional[str] = None


class Farm(BaseModel):
    """Farm response model"""
    id: str
    user_id: str
    name: str
    crop_type: str
    latitude: float
    longitude: float
    area: Optional[float]
    location_address: Optional[str]
    created_at: str
    updated_at: str


# =====================================================
# API Endpoints
# =====================================================

@router.get("/farms", response_model=List[Farm])
async def get_farms(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    limit: int = 100
):
    """
    Get all farms for a user
    Args:
        user_id: User identifier (default: test user)
        limit: Maximum number of farms to return
    Returns:
        List of farms
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("farms")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        logger.info(f"Retrieved {len(response.data)} farms for user {user_id}")
        
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching farms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch farms: {str(e)}")


@router.get("/farms/{farm_id}", response_model=Farm)
async def get_farm(farm_id: str):
    """
    Get a specific farm by ID
    Args:
        farm_id: Farm identifier
    Returns:
        Farm details
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("farms")\
            .select("*")\
            .eq("id", farm_id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        logger.info(f"Retrieved farm {farm_id}")
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch farm: {str(e)}")


@router.post("/farms", response_model=Farm, status_code=201)
async def create_farm(farm: FarmCreate):
    """
    Create a new farm
    Args:
        farm: Farm data
    Returns:
        Created farm with ID
    """
    try:
        supabase = get_supabase_client()
        
        # Prepare farm data
        farm_data = {
            "user_id": farm.user_id,
            "name": farm.name,
            "crop_type": farm.crop_type.lower(),
            "latitude": farm.latitude,
            "longitude": farm.longitude,
            "area": farm.area,
            "location_address": farm.location_address
        }
        
        response = supabase.table("farms")\
            .insert(farm_data)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create farm")
        
        created_farm = response.data[0]
        logger.info(f"Created farm: {created_farm['id']} - {created_farm['name']}")
        
        return created_farm
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating farm: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create farm: {str(e)}")


@router.put("/farms/{farm_id}", response_model=Farm)
async def update_farm(farm_id: str, farm_update: FarmUpdate):
    """
    Update an existing farm
    Args:
        farm_id: Farm identifier
        farm_update: Fields to update
    Returns:
        Updated farm
    """
    try:
        supabase = get_supabase_client()
        
        # Only include non-None fields
        update_data = {
            k: v for k, v in farm_update.dict().items() 
            if v is not None
        }
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Normalize crop_type if present
        if "crop_type" in update_data:
            update_data["crop_type"] = update_data["crop_type"].lower()
        
        response = supabase.table("farms")\
            .update(update_data)\
            .eq("id", farm_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        updated_farm = response.data[0]
        logger.info(f"Updated farm {farm_id}")
        
        return updated_farm
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update farm: {str(e)}")


@router.delete("/farms/{farm_id}")
async def delete_farm(farm_id: str):
    """
    Delete a farm
    Args:
        farm_id: Farm identifier
    Returns:
        Success message
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("farms")\
            .delete()\
            .eq("id", farm_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        logger.info(f"Deleted farm {farm_id}")
        
        return {
            "success": True,
            "message": f"Farm {farm_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete farm: {str(e)}")


@router.get("/farms/{farm_id}/latest-analysis")
async def get_latest_analysis(farm_id: str):
    """
    Get the most recent satellite analysis for a farm
    Args:
        farm_id: Farm identifier
    Returns:
        Latest analysis data or None
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("satellite_analysis")\
            .select("*")\
            .eq("farm_id", farm_id)\
            .order("analyzed_at", desc=True)\
            .limit(1)\
            .execute()
        
        if not response.data:
            logger.info(f"No analysis found for farm {farm_id}")
            return {
                "success": True,
                "data": None,
                "message": "No analysis available yet"
            }
        
        latest = response.data[0]
        logger.info(f"Retrieved latest analysis for farm {farm_id}")
        
        return {
            "success": True,
            "data": latest
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest analysis for farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis: {str(e)}")


@router.get("/farms/{farm_id}/stats")
async def get_farm_stats(farm_id: str):
    """
    Get statistics and summary for a farm
    Args:
        farm_id: Farm identifier
    Returns:
        Farm statistics including analysis count, avg health score, etc.
    """
    try:
        supabase = get_supabase_client()
        
        # Get farm details
        farm_response = supabase.table("farms")\
            .select("*")\
            .eq("id", farm_id)\
            .single()\
            .execute()
        
        if not farm_response.data:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        # Get analysis count and stats
        analysis_response = supabase.table("satellite_analysis")\
            .select("health_score, analyzed_at")\
            .eq("farm_id", farm_id)\
            .execute()
        
        analyses = analysis_response.data
        
        # Calculate stats
        stats = {
            "farm": farm_response.data,
            "total_analyses": len(analyses),
            "avg_health_score": None,
            "latest_health_score": None,
            "last_analyzed": None
        }
        
        if analyses:
            scores = [a["health_score"] for a in analyses if a["health_score"] is not None]
            if scores:
                stats["avg_health_score"] = round(sum(scores) / len(scores), 2)
                stats["latest_health_score"] = analyses[0]["health_score"]
            stats["last_analyzed"] = analyses[0]["analyzed_at"]
        
        logger.info(f"Retrieved stats for farm {farm_id}")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats for farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
