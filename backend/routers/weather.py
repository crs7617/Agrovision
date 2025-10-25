from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from services.weather_service import (
    get_current_weather,
    get_forecast,
    analyze_stress_correlation,
    WeatherData,
    ForecastDay
)
from services.knowledge_base import get_crop_info
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/weather/{farm_id}")
async def get_farm_weather(
    farm_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude")
):
    """
    Get current weather for farm location
    Args:
        farm_id: Farm identifier
        lat: Latitude
        lon: Longitude
    Returns:
        Current weather conditions
    """
    try:
        weather = get_current_weather(lat, lon)
        
        if not weather:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        return {
            "farm_id": farm_id,
            "location": {"lat": lat, "lon": lon},
            "weather": weather.to_dict(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather for farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/{farm_id}/forecast")
async def get_farm_forecast(
    farm_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days")
):
    """
    Get weather forecast for farm location
    Args:
        farm_id: Farm identifier
        lat: Latitude
        lon: Longitude
        days: Number of days (1-7)
    Returns:
        Weather forecast
    """
    try:
        forecast = get_forecast(lat, lon, days)
        
        if not forecast:
            raise HTTPException(status_code=503, detail="Forecast service unavailable")
        
        # Calculate summary statistics
        avg_temp = sum(day.temp_max for day in forecast) / len(forecast)
        total_rain = sum(day.rainfall_amount for day in forecast)
        high_rain_days = sum(1 for day in forecast if day.rainfall_prob > 60)
        
        return {
            "farm_id": farm_id,
            "location": {"lat": lat, "lon": lon},
            "forecast_days": days,
            "forecast": [day.to_dict() for day in forecast],
            "summary": {
                "avg_temperature": round(avg_temp, 1),
                "total_rainfall_expected": round(total_rain, 1),
                "rainy_days": high_rain_days
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching forecast for farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/{farm_id}/impact")
async def get_weather_impact(
    farm_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    crop_type: str = Query("wheat", description="Crop type"),
    current_ndvi: Optional[float] = Query(None, ge=0, le=1, description="Current NDVI value")
):
    """
    Analyze weather impact on crops
    Args:
        farm_id: Farm identifier
        lat: Latitude
        lon: Longitude
        crop_type: Type of crop
        current_ndvi: Current NDVI value (optional)
    Returns:
        Weather impact analysis and recommendations
    """
    try:
        # Get current weather and forecast
        current = get_current_weather(lat, lon)
        forecast = get_forecast(lat, lon, 7)
        
        if not current or not forecast:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        # Get crop-specific info
        crop_info = get_crop_info(crop_type)
        
        # Analyze impacts
        impacts = []
        recommendations = []
        risk_level = "low"
        
        # Check current conditions
        if current.temperature > 35:
            impacts.append({
                "type": "heat_stress",
                "severity": "high",
                "description": f"High temperature ({current.temperature}°C) may cause heat stress"
            })
            recommendations.append("Consider irrigation to cool plants")
            risk_level = "high"
        
        if current.humidity < 30:
            impacts.append({
                "type": "dry_air",
                "severity": "moderate",
                "description": f"Low humidity ({current.humidity}%) increases water stress"
            })
            if risk_level == "low":
                risk_level = "moderate"
        
        if current.rainfall > 30:
            impacts.append({
                "type": "heavy_rain",
                "severity": "moderate",
                "description": f"Heavy rainfall ({current.rainfall}mm) detected"
            })
            recommendations.append("Check for waterlogging in low areas")
        
        # Check forecast
        hot_days = sum(1 for day in forecast if day.temp_max > 35)
        dry_days = sum(1 for day in forecast if day.rainfall_prob < 20)
        rainy_days = sum(1 for day in forecast if day.rainfall_prob > 70)
        
        if hot_days >= 3:
            impacts.append({
                "type": "prolonged_heat",
                "severity": "high",
                "description": f"{hot_days} days with temperatures >35°C expected"
            })
            recommendations.append(f"Plan irrigation schedule for next {hot_days} days")
            risk_level = "high"
        
        if dry_days >= 5 and crop_info["water_needs"] == "high":
            impacts.append({
                "type": "water_scarcity",
                "severity": "high",
                "description": f"{dry_days} dry days ahead for high water-need crop"
            })
            recommendations.append("Ensure adequate water supply for irrigation")
            risk_level = "high"
        
        if rainy_days >= 3:
            impacts.append({
                "type": "excess_moisture",
                "severity": "moderate",
                "description": f"{rainy_days} rainy days expected - risk of disease"
            })
            recommendations.append("Monitor for fungal diseases")
            if risk_level == "low":
                risk_level = "moderate"
        
        # NDVI-based analysis
        if current_ndvi is not None:
            ndvi_min, ndvi_max = crop_info["optimal_ndvi"]
            if current_ndvi < ndvi_min * 0.8:
                impacts.append({
                    "type": "crop_stress",
                    "severity": "high",
                    "description": f"Low NDVI ({current_ndvi:.2f}) with current weather conditions"
                })
                if current.rainfall < 5 and dry_days >= 3:
                    recommendations.append("Immediate irrigation recommended - crop already stressed")
                    risk_level = "critical"
        
        if not impacts:
            impacts.append({
                "type": "favorable",
                "severity": "none",
                "description": "Weather conditions are favorable for crop growth"
            })
            recommendations.append("Continue regular monitoring")
        
        return {
            "farm_id": farm_id,
            "crop_type": crop_type,
            "current_weather": current.to_dict(),
            "forecast_summary": {
                "hot_days": hot_days,
                "dry_days": dry_days,
                "rainy_days": rainy_days
            },
            "risk_level": risk_level,
            "impacts": impacts,
            "recommendations": recommendations,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing weather impact for farm {farm_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/test")
async def test_weather():
    """Test endpoint for weather router"""
    return {"message": "Weather router working", "status": "ok"}
