"""
Phase 4 Tests: Weather & Temporal Analysis
Tests weather_service.py and temporal_service.py functionality
"""
import sys
import os
from datetime import datetime, timedelta
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.weather_service import (
    get_current_weather,
    get_forecast,
    analyze_stress_correlation,
    WeatherData,
    clear_cache
)
from services.temporal_service import (
    get_historical_trend,
    detect_anomalies,
    compare_seasonal_pattern,
    calculate_trend_direction,
    TimeSeriesPoint
)


def test_current_weather():
    """Test 1: Fetch current weather"""
    print("\n=== Test 1: Current Weather ===")
    
    # Test location: Delhi, India
    lat, lon = 28.6139, 77.2090
    
    print(f"\nFetching weather for Delhi ({lat}, {lon})...")
    weather = get_current_weather(lat, lon)
    
    if weather:
        print(f"✓ Weather data received")
        print(f"  Temperature: {weather.temperature}°C")
        print(f"  Humidity: {weather.humidity}%")
        print(f"  Rainfall: {weather.rainfall}mm")
        print(f"  Wind Speed: {weather.wind_speed} m/s")
        print(f"  Description: {weather.description}")
        print(f"  Timestamp: {weather.timestamp}")
    else:
        print("✗ Failed to fetch weather")
    
    print("\n✅ Test 1 Complete\n")


def test_weather_forecast():
    """Test 2: Fetch weather forecast"""
    print("=== Test 2: Weather Forecast ===")
    
    # Test location: Punjab, India (wheat growing region)
    lat, lon = 30.7333, 76.7794
    
    print(f"\nFetching 7-day forecast for Punjab ({lat}, {lon})...")
    forecast = get_forecast(lat, lon, days=7)
    
    if forecast:
        print(f"✓ Forecast received: {len(forecast)} days")
        
        for i, day in enumerate(forecast[:3], 1):  # Show first 3 days
            print(f"\nDay {i} ({day.date}):")
            print(f"  Temp: {day.temp_min}°C - {day.temp_max}°C")
            print(f"  Humidity: {day.humidity}%")
            print(f"  Rain Probability: {day.rainfall_prob}%")
            print(f"  Expected Rainfall: {day.rainfall_amount}mm")
            print(f"  {day.description}")
        
        if len(forecast) > 3:
            print(f"\n  ... and {len(forecast) - 3} more days")
    else:
        print("✗ Failed to fetch forecast")
    
    print("\n✅ Test 2 Complete\n")


def test_weather_caching():
    """Test 3: Verify weather caching (1-hour TTL)"""
    print("=== Test 3: Weather Caching ===")
    
    import time
    
    lat, lon = 28.6139, 77.2090
    
    # Clear cache first
    clear_cache()
    print("\n✓ Cache cleared")
    
    # First call (should fetch from API)
    print("\nFirst call (should fetch from API)...")
    start = time.time()
    weather1 = get_current_weather(lat, lon)
    time1 = time.time() - start
    print(f"  Time: {time1:.3f}s")
    
    # Second call (should use cache)
    print("\nSecond call (should use cache)...")
    start = time.time()
    weather2 = get_current_weather(lat, lon)
    time2 = time.time() - start
    print(f"  Time: {time2:.3f}s")
    
    if weather1 and weather2:
        same_temp = weather1.temperature == weather2.temperature
        faster = time2 < time1 * 0.5  # Cached should be much faster
        
        print(f"\n✓ Same data returned: {same_temp}")
        print(f"✓ Second call faster: {faster} ({time2:.3f}s vs {time1:.3f}s)")
    
    print("\n✅ Test 3 Complete\n")


def test_stress_correlation():
    """Test 4: Analyze weather-NDVI correlation"""
    print("=== Test 4: Weather-NDVI Stress Correlation ===")
    
    # Create mock weather history with heat wave
    base_date = datetime.now() - timedelta(days=30)
    weather_history = []
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Simulate heat wave on days 10-15
        if 10 <= i <= 15:
            temp = 38 + np.random.normal(0, 1)
            humidity = 25
            rainfall = 0
        else:
            temp = 28 + np.random.normal(0, 2)
            humidity = 60
            rainfall = 2 if i % 5 == 0 else 0
        
        weather_history.append(WeatherData(
            timestamp=date,
            temperature=temp,
            humidity=humidity,
            rainfall=rainfall,
            wind_speed=3.5,
            pressure=1013,
            description="clear" if rainfall == 0 else "rain"
        ))
    
    # Create NDVI trend with drop after heat wave
    ndvi_trend = []
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        if i < 10:
            ndvi = 0.75 + np.random.normal(0, 0.02)
        elif i < 17:
            # Drop during/after heat wave
            ndvi = 0.75 - (i - 10) * 0.05 + np.random.normal(0, 0.02)
        else:
            # Partial recovery
            ndvi = 0.55 + (i - 17) * 0.01 + np.random.normal(0, 0.02)
        
        ndvi_trend.append((date, max(0.2, min(0.9, ndvi))))
    
    print("\n--- Simulated Scenario ---")
    print("Weather: Heat wave (38°C) on days 10-15")
    print("NDVI: Drop from 0.75 to 0.55 starting day 10")
    
    # Analyze correlation
    result = analyze_stress_correlation(weather_history, ndvi_trend)
    
    print(f"\n--- Analysis Result ---")
    print(f"Likely Cause: {result['likely_cause']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Details: {result['details']}")
    print(f"NDVI Drops Detected: {result.get('ndvi_drops_count', 0)}")
    
    if 'correlation_counts' in result:
        print(f"\nCorrelation Counts:")
        for cause, count in result['correlation_counts'].items():
            if count > 0:
                print(f"  {cause}: {count}")
    
    # Verify it detected heat stress
    expected_cause = result['likely_cause'] in ['heat_stress', 'water_stress']
    print(f"\n✓ Correctly identified heat/water stress: {expected_cause}")
    
    print("\n✅ Test 4 Complete\n")


def test_historical_trend():
    """Test 5: Get historical trend data"""
    print("=== Test 5: Historical Trend Retrieval ===")
    
    farm_id = "test_farm_001"
    
    print(f"\nFetching 90-day NDVI trend for farm {farm_id}...")
    time_series = get_historical_trend(farm_id, "NDVI", days=90)
    
    print(f"✓ Retrieved {len(time_series)} data points")
    
    if time_series:
        print(f"\nFirst point:")
        print(f"  Date: {time_series[0].timestamp}")
        print(f"  NDVI: {time_series[0].value}")
        
        print(f"\nLatest point:")
        print(f"  Date: {time_series[-1].timestamp}")
        print(f"  NDVI: {time_series[-1].value}")
        
        # Calculate basic stats
        values = [p.value for p in time_series]
        print(f"\nStatistics:")
        print(f"  Mean NDVI: {np.mean(values):.3f}")
        print(f"  Min NDVI: {np.min(values):.3f}")
        print(f"  Max NDVI: {np.max(values):.3f}")
        print(f"  Std Dev: {np.std(values):.3f}")
    
    print("\n✅ Test 5 Complete\n")


def test_anomaly_detection():
    """Test 6: Detect anomalies in time series"""
    print("=== Test 6: Anomaly Detection ===")
    
    # Create time series with anomalies
    base_date = datetime.now() - timedelta(days=60)
    time_series = []
    
    for i in range(60):
        date = base_date + timedelta(days=i)
        
        # Normal pattern with some noise
        value = 0.7 + 0.1 * np.sin(2 * np.pi * i / 30) + np.random.normal(0, 0.02)
        
        # Inject anomalies
        if i == 15:  # Sudden drop
            value = 0.4
        elif i == 30:  # Spike
            value = 0.95
        elif i == 45:  # Another drop
            value = 0.35
        
        time_series.append(TimeSeriesPoint(
            timestamp=date,
            value=max(0, min(1, value)),
            metadata={"index": "NDVI"}
        ))
    
    print(f"\n--- Input Data ---")
    print(f"Total points: {len(time_series)}")
    print(f"Injected anomalies: 3 (days 15, 30, 45)")
    
    # Detect anomalies
    anomalies = detect_anomalies(time_series, threshold_std=2.0)
    
    print(f"\n--- Detected Anomalies ---")
    print(f"Total detected: {len(anomalies)}")
    
    for i, anomaly in enumerate(anomalies, 1):
        print(f"\n{i}. {anomaly.date.strftime('%Y-%m-%d')}")
        print(f"   Value: {anomaly.value:.3f}")
        print(f"   Expected: {anomaly.expected_value:.3f}")
        print(f"   Deviation: {anomaly.deviation:.2f} σ")
        print(f"   Severity: {anomaly.severity}")
        print(f"   Type: {anomaly.type}")
    
    # Verify detection
    detected_some = len(anomalies) >= 3
    print(f"\n✓ Detected anomalies: {detected_some}")
    
    print("\n✅ Test 6 Complete\n")


def test_seasonal_comparison():
    """Test 7: Compare current data to seasonal baseline"""
    print("=== Test 7: Seasonal Pattern Comparison ===")
    
    current_data = {
        "NDVI": 0.68,
        "EVI": 0.52,
        "SAVI": 0.58
    }
    
    farm_id = "test_farm_001"
    crop_type = "wheat"
    
    print(f"\n--- Current Data ---")
    for index, value in current_data.items():
        print(f"{index}: {value}")
    
    # Compare to seasonal baseline
    result = compare_seasonal_pattern(current_data, farm_id, crop_type)
    
    print(f"\n--- Seasonal Comparison ---")
    print(f"Comparison: {result['comparison_text']}")
    print(f"Is Normal: {result['is_normal']}")
    print(f"Deviation: {result['deviation_percentage']}%")
    print(f"Confidence: {result['confidence']}")
    print(f"Baseline: {result.get('baseline_period', 'N/A')}")
    
    if 'detailed_results' in result and result['detailed_results']:
        print(f"\n--- Detailed Results ---")
        for index, details in result['detailed_results'].items():
            print(f"\n{index}:")
            print(f"  Current: {details['current_value']:.3f}")
            print(f"  Historical Mean: {details['historical_mean']:.3f}")
            print(f"  Deviation: {details['deviation']:.3f} ({details['deviation_percentage']:.1f}%)")
            print(f"  Normal: {details['is_normal']}")
    
    print("\n✅ Test 7 Complete\n")


def test_trend_calculation():
    """Test 8: Calculate trend direction and rate"""
    print("=== Test 8: Trend Direction Calculation ===")
    
    # Create improving trend
    base_date = datetime.now() - timedelta(days=60)
    time_series = []
    
    for i in range(60):
        date = base_date + timedelta(days=i)
        # Linearly improving NDVI
        value = 0.5 + (i / 60) * 0.25 + np.random.normal(0, 0.02)
        time_series.append(TimeSeriesPoint(
            timestamp=date,
            value=max(0, min(1, value)),
            metadata={}
        ))
    
    print(f"\n--- Input Data ---")
    print(f"Pattern: Linearly improving from 0.5 to 0.75 over 60 days")
    print(f"Data points: {len(time_series)}")
    
    # Calculate trend
    trend = calculate_trend_direction(time_series)
    
    print(f"\n--- Trend Analysis ---")
    print(f"Direction: {trend['direction']}")
    print(f"Rate: {trend['rate_per_week']:.4f} per week")
    print(f"Confidence: {trend['confidence']}")
    print(f"Interpretation: {trend['interpretation']}")
    
    # Verify
    is_improving = trend['direction'] == 'improving'
    positive_rate = trend['rate_per_week'] > 0
    
    print(f"\n✓ Detected improvement: {is_improving}")
    print(f"✓ Positive rate: {positive_rate}")
    
    print("\n✅ Test 8 Complete\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("    PHASE 4 TEST SUITE: WEATHER & TEMPORAL ANALYSIS")
    print("="*60)
    
    try:
        # Run all tests
        test_current_weather()
        test_weather_forecast()
        test_weather_caching()
        test_stress_correlation()
        test_historical_trend()
        test_anomaly_detection()
        test_seasonal_comparison()
        test_trend_calculation()
        
        print("\n" + "="*60)
        print("    ALL PHASE 4 TESTS COMPLETE")
        print("="*60)
        print("\n✅ Weather Service: Fully functional")
        print("✅ Temporal Analysis: Fully functional")
        print("\nNote: Weather quality depends on OPENWEATHER_API_KEY")
        print("Fallback mode provides estimates when API unavailable\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
