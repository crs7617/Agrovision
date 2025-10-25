"""Quick test of real weather API"""
import os
from dotenv import load_dotenv

# Force reload environment
load_dotenv(override=True)

print(f"API Key loaded: {os.getenv('OPENWEATHER_API_KEY')[:10]}...")

from services.weather_service import get_current_weather, get_forecast

# Test Delhi
print("\n=== Testing Delhi Weather ===")
weather = get_current_weather(28.6139, 77.2090)
print(f"Temperature: {weather.temperature}°C")
print(f"Humidity: {weather.humidity}%")
print(f"Description: {weather.description}")
print(f"Rainfall: {weather.rainfall}mm")

# Test Forecast
print("\n=== Testing Punjab Forecast ===")
forecast = get_forecast(30.7333, 76.7794, days=5)
print(f"Forecast days: {len(forecast)}")
for i, day in enumerate(forecast[:3], 1):
    print(f"\nDay {i} ({day.date}):")
    print(f"  Temp: {day.temp_min}°C - {day.temp_max}°C")
    print(f"  Rain: {day.rainfall_prob}%")
    print(f"  {day.description}")
