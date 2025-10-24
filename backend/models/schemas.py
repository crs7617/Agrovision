from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class FarmRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: str = Field(..., min_length=1)
    area_hectares: float = Field(..., gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Green Valley Farm",
                "latitude": 17.45,
                "longitude": 78.35,
                "crop_type": "rice",
                "area_hectares": 2.5
            }
        }

class AnalysisResponse(BaseModel):
    analysis_id: str
    farm_id: str
    analysis_date: datetime
    ndvi_mean: float
    evi_mean: float
    health_score: float
    health_category: str
    all_indices: Dict[str, float]
    visualization_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "farm_id": "farm_123",
                "analysis_date": "2024-01-15T10:30:00",
                "ndvi_mean": 0.65,
                "evi_mean": 0.55,
                "health_score": 0.75,
                "health_category": "Good",
                "all_indices": {"NDVI": 0.65, "EVI": 0.55},
                "visualization_url": "https://storage.url/image.png"
            }
        }

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    farm_id: Optional[str] = None
    context: Optional[Dict] = None

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
