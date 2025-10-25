"""
Weather Service using OpenWeatherMap API
Fetches weather data and analyzes correlation with crop health
"""
import os
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

# Cache for weather data (1 hour TTL)
_weather_cache = {}
_cache_ttl = 3600  # 1 hour in seconds


@dataclass
class WeatherData:
    """Structured weather data"""
    timestamp: datetime
    temperature: float  # Celsius
    humidity: float  # percentage
    rainfall: float  # mm
    wind_speed: float  # m/s
    pressure: float  # hPa
    description: str
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature,
            "humidity": self.humidity,
            "rainfall": self.rainfall,
            "wind_speed": self.wind_speed,
            "pressure": self.pressure,
            "description": self.description
        }


@dataclass
class ForecastDay:
    """Daily forecast summary"""
    date: str
    temp_min: float
    temp_max: float
    humidity: float
    rainfall_prob: float  # percentage
    rainfall_amount: float  # mm
    description: str
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "temp_min": self.temp_min,
            "temp_max": self.temp_max,
            "humidity": self.humidity,
            "rainfall_prob": self.rainfall_prob,
            "rainfall_amount": self.rainfall_amount,
            "description": self.description
        }


def _get_api_key() -> Optional[str]:
    """Get OpenWeatherMap API key from environment"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key or api_key == "":
        logger.warning("OPENWEATHER_API_KEY not set - weather features unavailable")
        return None
    return api_key


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid (within TTL)"""
    if cache_key not in _weather_cache:
        return False
    
    cached_data = _weather_cache[cache_key]
    cache_time = cached_data.get("timestamp", 0)
    
    return (time.time() - cache_time) < _cache_ttl


def get_current_weather(lat: float, lon: float) -> Optional[WeatherData]:
    """
    Fetch current weather conditions
    Args:
        lat: Latitude
        lon: Longitude
    Returns:
        WeatherData object or None if error
    """
    cache_key = f"current_{lat}_{lon}"
    
    # Check cache first
    if _is_cache_valid(cache_key):
        logger.info("Returning cached weather data")
        return _weather_cache[cache_key]["data"]
    
    api_key = _get_api_key()
    if not api_key:
        return _get_fallback_weather(lat, lon)
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"  # Celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract weather data
        weather = WeatherData(
            timestamp=datetime.now(),
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            rainfall=data.get("rain", {}).get("1h", 0.0),  # Last hour rainfall
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
            description=data["weather"][0]["description"]
        )
        
        # Cache the result
        _weather_cache[cache_key] = {
            "data": weather,
            "timestamp": time.time()
        }
        
        logger.info(f"Fetched weather for ({lat}, {lon}): {weather.temperature}°C, {weather.description}")
        return weather
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather: {e}")
        return _get_fallback_weather(lat, lon)
    except Exception as e:
        logger.error(f"Unexpected error in get_current_weather: {e}")
        return _get_fallback_weather(lat, lon)


def get_forecast(lat: float, lon: float, days: int = 7) -> List[ForecastDay]:
    """
    Get 7-day weather forecast
    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days (max 7)
    Returns:
        List of ForecastDay objects
    """
    cache_key = f"forecast_{lat}_{lon}_{days}"
    
    # Check cache
    if _is_cache_valid(cache_key):
        logger.info("Returning cached forecast data")
        return _weather_cache[cache_key]["data"]
    
    api_key = _get_api_key()
    if not api_key:
        return _get_fallback_forecast(lat, lon, days)
    
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast/daily"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "cnt": min(days, 7)  # Max 7 days for free tier
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # If daily forecast not available (free tier limitation), use 5-day/3-hour forecast
        if response.status_code == 401:
            return _get_forecast_from_hourly(lat, lon, days, api_key)
        
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        for day_data in data["list"]:
            forecast_day = ForecastDay(
                date=datetime.fromtimestamp(day_data["dt"]).strftime("%Y-%m-%d"),
                temp_min=day_data["temp"]["min"],
                temp_max=day_data["temp"]["max"],
                humidity=day_data["humidity"],
                rainfall_prob=day_data.get("pop", 0) * 100,  # Probability of precipitation
                rainfall_amount=day_data.get("rain", 0),
                description=day_data["weather"][0]["description"]
            )
            forecast.append(forecast_day)
        
        # Cache the result
        _weather_cache[cache_key] = {
            "data": forecast,
            "timestamp": time.time()
        }
        
        logger.info(f"Fetched {len(forecast)}-day forecast for ({lat}, {lon})")
        return forecast
        
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        return _get_fallback_forecast(lat, lon, days)


def _get_forecast_from_hourly(lat: float, lon: float, days: int, api_key: str) -> List[ForecastDay]:
    """
    Get forecast from 5-day/3-hour data (free tier fallback)
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Group by day
        daily_data = {}
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            
            if date not in daily_data:
                daily_data[date] = {
                    "temps": [],
                    "humidity": [],
                    "rain": 0,
                    "descriptions": []
                }
            
            daily_data[date]["temps"].append(item["main"]["temp"])
            daily_data[date]["humidity"].append(item["main"]["humidity"])
            daily_data[date]["rain"] += item.get("rain", {}).get("3h", 0)
            daily_data[date]["descriptions"].append(item["weather"][0]["description"])
        
        # Convert to ForecastDay objects
        forecast = []
        for date in sorted(daily_data.keys())[:days]:
            day = daily_data[date]
            forecast.append(ForecastDay(
                date=date,
                temp_min=min(day["temps"]),
                temp_max=max(day["temps"]),
                humidity=sum(day["humidity"]) / len(day["humidity"]),
                rainfall_prob=50 if day["rain"] > 0 else 20,  # Estimate
                rainfall_amount=day["rain"],
                description=max(set(day["descriptions"]), key=day["descriptions"].count)
            ))
        
        return forecast
        
    except Exception as e:
        logger.error(f"Error in hourly forecast fallback: {e}")
        return _get_fallback_forecast(lat, lon, days)


def analyze_stress_correlation(
    weather_history: List[WeatherData],
    ndvi_trend: List[Tuple[datetime, float]]
) -> Dict:
    """
    Analyze correlation between weather events and NDVI drops
    Args:
        weather_history: List of historical weather data
        ndvi_trend: List of (timestamp, ndvi_value) tuples
    Returns:
        Dictionary with likely_cause, confidence, and details
    """
    if not weather_history or not ndvi_trend:
        return {
            "likely_cause": "insufficient_data",
            "confidence": 0.0,
            "details": "Not enough data for correlation analysis"
        }
    
    # Detect NDVI drops (>10% decrease)
    ndvi_drops = []
    for i in range(1, len(ndvi_trend)):
        prev_ndvi = ndvi_trend[i-1][1]
        curr_ndvi = ndvi_trend[i][1]
        
        if prev_ndvi > 0 and (prev_ndvi - curr_ndvi) / prev_ndvi > 0.1:
            ndvi_drops.append({
                "date": ndvi_trend[i][0],
                "drop_percentage": ((prev_ndvi - curr_ndvi) / prev_ndvi) * 100,
                "ndvi_value": curr_ndvi
            })
    
    if not ndvi_drops:
        return {
            "likely_cause": "no_stress_detected",
            "confidence": 0.9,
            "details": "NDVI trend is stable with no significant drops"
        }
    
    # Analyze weather patterns around drop dates
    correlations = {
        "heat_stress": 0,
        "water_stress": 0,
        "heavy_rain": 0,
        "wind_damage": 0
    }
    
    for drop in ndvi_drops:
        drop_date = drop["date"]
        
        # Check weather 1-7 days before drop
        for weather in weather_history:
            days_before = (drop_date - weather.timestamp).days
            
            if 1 <= days_before <= 7:
                # Heat stress (>35°C)
                if weather.temperature > 35:
                    correlations["heat_stress"] += 1
                
                # Water stress (high temp + low humidity + no rain)
                if weather.temperature > 30 and weather.humidity < 40 and weather.rainfall < 1:
                    correlations["water_stress"] += 1
                
                # Heavy rain (>50mm)
                if weather.rainfall > 50:
                    correlations["heavy_rain"] += 1
                
                # Strong wind (>15 m/s)
                if weather.wind_speed > 15:
                    correlations["wind_damage"] += 1
    
    # Determine most likely cause
    if not any(correlations.values()):
        return {
            "likely_cause": "unknown",
            "confidence": 0.3,
            "details": "NDVI drop detected but no clear weather correlation found"
        }
    
    likely_cause = max(correlations, key=correlations.get)
    total_correlations = sum(correlations.values())
    confidence = correlations[likely_cause] / total_correlations
    
    cause_descriptions = {
        "heat_stress": "High temperatures (>35°C) detected before NDVI drop",
        "water_stress": "Hot, dry conditions with low rainfall preceded stress",
        "heavy_rain": "Heavy rainfall events may have caused waterlogging",
        "wind_damage": "Strong winds detected, possible physical crop damage"
    }
    
    return {
        "likely_cause": likely_cause,
        "confidence": confidence,
        "details": cause_descriptions[likely_cause],
        "ndvi_drops_count": len(ndvi_drops),
        "correlation_counts": correlations
    }


def _get_fallback_weather(lat: float, lon: float) -> WeatherData:
    """
    Fallback weather data when API unavailable
    Generates reasonable estimates based on location
    """
    # Simple estimation based on latitude
    base_temp = 25 - abs(lat) * 0.5  # Cooler at higher latitudes
    
    return WeatherData(
        timestamp=datetime.now(),
        temperature=base_temp + 5,  # Add some variation
        humidity=60,
        rainfall=0,
        wind_speed=3.5,
        pressure=1013,
        description="Estimated conditions (API unavailable)"
    )


def _get_fallback_forecast(lat: float, lon: float, days: int) -> List[ForecastDay]:
    """
    Fallback forecast when API unavailable
    """
    forecast = []
    base_temp = 25 - abs(lat) * 0.5
    
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        forecast.append(ForecastDay(
            date=date,
            temp_min=base_temp - 3,
            temp_max=base_temp + 5,
            humidity=60,
            rainfall_prob=30,
            rainfall_amount=0,
            description="Estimated forecast (API unavailable)"
        ))
    
    return forecast


def clear_cache():
    """Clear weather cache (for testing)"""
    global _weather_cache
    _weather_cache = {}
    logger.info("Weather cache cleared")
