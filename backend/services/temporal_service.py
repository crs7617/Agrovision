"""
Temporal Analysis Service
Historical pattern analysis and anomaly detection for crop health monitoring
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
import logging
from services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesPoint:
    """Single point in time series"""
    timestamp: datetime
    value: float
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata or {}
        }


@dataclass
class Anomaly:
    """Detected anomaly in time series"""
    date: datetime
    value: float
    expected_value: float
    deviation: float  # Standard deviations from mean
    severity: str  # "minor", "moderate", "severe"
    type: str  # "drop", "spike"
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "value": self.value,
            "expected_value": self.expected_value,
            "deviation": round(self.deviation, 2),
            "severity": self.severity,
            "type": self.type
        }


def get_historical_trend(
    farm_id: str,
    index_name: str,
    days: int = 90,
    mock_data: Optional[List[Dict]] = None
) -> List[TimeSeriesPoint]:
    """
    Get historical trend for a spectral index
    Args:
        farm_id: Farm identifier
        index_name: Index to retrieve (NDVI, EVI, SAVI, etc.)
        days: Number of days to look back
        mock_data: Optional mock data for testing (list of {date, value} dicts)
    Returns:
        List of TimeSeriesPoint objects
    """
    # If mock data provided (for testing), use it
    if mock_data:
        time_series = []
        for entry in mock_data:
            time_series.append(TimeSeriesPoint(
                timestamp=entry["date"] if isinstance(entry["date"], datetime) else datetime.fromisoformat(entry["date"]),
                value=entry["value"],
                metadata=entry.get("metadata", {})
            ))
        return time_series
    
    # Try to load from database first
    try:
        supabase = get_supabase_client()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = supabase.table("temporal_data")\
            .select("*")\
            .eq("farm_id", farm_id)\
            .eq("metric_type", index_name.upper())\
            .gte("timestamp", cutoff_date.isoformat())\
            .order("timestamp", desc=False)\
            .execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"✓ Retrieved {len(result.data)} historical data points from database")
            time_series = []
            for row in result.data:
                time_series.append(TimeSeriesPoint(
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    value=float(row["value"]),
                    metadata={
                        "is_anomaly": row.get("is_anomaly", False),
                        "anomaly_type": row.get("anomaly_type")
                    }
                ))
            return time_series
        else:
            logger.info(f"No historical data in database for farm {farm_id}, generating mock data")
    
    except Exception as e:
        logger.warning(f"Failed to load from database: {e}, using mock data")
    
    # Generate mock historical data for demonstration
    logger.info(f"Using mock data for farm {farm_id} - {index_name}")
    
    time_series = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate synthetic data with seasonal variation
    num_points = min(days // 7, 52)  # Weekly data points
    
    for i in range(num_points):
        date = start_date + timedelta(days=i * 7)
        
        # Simulate NDVI-like pattern with seasonal variation
        base_value = 0.65
        seasonal = 0.15 * np.sin(2 * np.pi * i / 52)  # Annual cycle
        noise = np.random.normal(0, 0.05)
        
        # Simulate growth stages
        if index_name.upper() == "NDVI":
            value = max(0.2, min(0.9, base_value + seasonal + noise))
        elif index_name.upper() == "EVI":
            value = max(0.1, min(0.7, (base_value + seasonal + noise) * 0.7))
        elif index_name.upper() == "SAVI":
            value = max(0.15, min(0.75, (base_value + seasonal + noise) * 0.8))
        else:
            value = 0.5 + np.random.normal(0, 0.1)
        
        time_series.append(TimeSeriesPoint(
            timestamp=date,
            value=round(value, 3),
            metadata={"index": index_name, "farm_id": farm_id}
        ))
    
    return time_series


def detect_anomalies(
    time_series_data: List[TimeSeriesPoint],
    threshold_std: float = 2.0
) -> List[Anomaly]:
    """
    Detect anomalies in time series data
    Args:
        time_series_data: List of TimeSeriesPoint objects
        threshold_std: Number of standard deviations for anomaly (default 2.0)
    Returns:
        List of detected anomalies
    """
    if len(time_series_data) < 3:
        logger.warning("Not enough data points for anomaly detection")
        return []
    
    # Extract values
    values = np.array([point.value for point in time_series_data])
    timestamps = [point.timestamp for point in time_series_data]
    
    # Calculate statistics
    mean = np.mean(values)
    std = np.std(values)
    
    if std == 0:
        logger.warning("Zero standard deviation - no anomalies detected")
        return []
    
    anomalies = []
    
    # Detect anomalies
    for i, (value, timestamp) in enumerate(zip(values, timestamps)):
        deviation = (value - mean) / std
        
        if abs(deviation) > threshold_std:
            # Determine severity
            if abs(deviation) > 3:
                severity = "severe"
            elif abs(deviation) > 2.5:
                severity = "moderate"
            else:
                severity = "minor"
            
            # Determine type
            anomaly_type = "spike" if deviation > 0 else "drop"
            
            anomalies.append(Anomaly(
                date=timestamp,
                value=value,
                expected_value=mean,
                deviation=abs(deviation),
                severity=severity,
                type=anomaly_type
            ))
    
    # Also detect sudden changes (rate of change)
    for i in range(1, len(values)):
        change = abs(values[i] - values[i-1])
        relative_change = change / (values[i-1] + 1e-6)
        
        # If change >20%, flag as potential anomaly
        if relative_change > 0.2:
            # Check if already flagged
            already_flagged = any(
                abs((a.date - timestamps[i]).total_seconds()) < 86400 
                for a in anomalies
            )
            
            if not already_flagged:
                change_type = "spike" if values[i] > values[i-1] else "drop"
                anomalies.append(Anomaly(
                    date=timestamps[i],
                    value=values[i],
                    expected_value=values[i-1],
                    deviation=relative_change * 100,  # As percentage
                    severity="moderate" if relative_change > 0.3 else "minor",
                    type=f"sudden_{change_type}"
                ))
    
    logger.info(f"Detected {len(anomalies)} anomalies in time series")
    return anomalies


def compare_seasonal_pattern(
    current_data: Dict[str, float],
    farm_id: str,
    crop_type: str,
    historical_data: Optional[List[TimeSeriesPoint]] = None
) -> Dict:
    """
    Compare current values to historical seasonal baseline
    Args:
        current_data: Current spectral indices
        farm_id: Farm identifier
        crop_type: Type of crop
        historical_data: Optional historical data for comparison
    Returns:
        Comparison analysis dictionary
    """
    # Get current month
    current_month = datetime.now().month
    
    # If no historical data provided, use mock/generate
    if not historical_data:
        # Generate last year's data for same period
        historical_data = get_historical_trend(farm_id, "NDVI", days=365)
    
    # Filter to same season (±1 month from current month)
    seasonal_data = []
    for point in historical_data:
        point_month = point.timestamp.month
        if abs(point_month - current_month) <= 1 or abs(point_month - current_month) >= 11:
            seasonal_data.append(point)
    
    if not seasonal_data:
        return {
            "comparison_text": "Insufficient historical data for seasonal comparison",
            "is_normal": True,
            "deviation_percentage": 0,
            "confidence": "low"
        }
    
    # Calculate historical baseline for each index
    results = {}
    
    for index_name, current_value in current_data.items():
        # Get historical values for this index
        if historical_data[0].metadata and historical_data[0].metadata.get("index") == index_name:
            hist_values = [p.value for p in seasonal_data]
        else:
            # If metadata not available, use all values
            hist_values = [p.value for p in seasonal_data]
        
        if not hist_values:
            continue
        
        baseline_mean = np.mean(hist_values)
        baseline_std = np.std(hist_values)
        
        # Calculate deviation
        deviation = current_value - baseline_mean
        deviation_percentage = (deviation / baseline_mean * 100) if baseline_mean > 0 else 0
        
        # Determine if normal (within 1.5 std)
        is_normal = abs(deviation) <= (1.5 * baseline_std)
        
        results[index_name] = {
            "current_value": current_value,
            "historical_mean": baseline_mean,
            "historical_std": baseline_std,
            "deviation": deviation,
            "deviation_percentage": deviation_percentage,
            "is_normal": is_normal
        }
    
    # Generate overall comparison text
    if not results:
        comparison_text = "No comparison data available"
        overall_normal = True
        overall_deviation = 0
    else:
        # Focus on NDVI for main comparison
        ndvi_result = results.get("NDVI", list(results.values())[0])
        
        deviation_pct = ndvi_result["deviation_percentage"]
        
        if abs(deviation_pct) < 10:
            comparison_text = f"Crop health is normal for this season (within {abs(deviation_pct):.1f}% of historical average)"
            overall_normal = True
        elif deviation_pct > 10:
            comparison_text = f"Crop health is {deviation_pct:.1f}% better than historical average for this season"
            overall_normal = True
        else:
            comparison_text = f"Crop health is {abs(deviation_pct):.1f}% below historical average - investigation recommended"
            overall_normal = False
        
        overall_deviation = deviation_pct
    
    return {
        "comparison_text": comparison_text,
        "is_normal": overall_normal,
        "deviation_percentage": round(overall_deviation, 1),
        "confidence": "high" if len(seasonal_data) > 5 else "medium",
        "baseline_period": f"{len(seasonal_data)} historical observations",
        "detailed_results": results
    }


def calculate_trend_direction(time_series_data: List[TimeSeriesPoint]) -> Dict:
    """
    Calculate trend direction (improving/declining) and rate
    Args:
        time_series_data: List of TimeSeriesPoint objects
    Returns:
        Trend analysis dictionary
    """
    if len(time_series_data) < 2:
        return {
            "direction": "unknown",
            "rate": 0,
            "confidence": "low"
        }
    
    # Use linear regression for trend
    values = np.array([p.value for p in time_series_data])
    timestamps = np.array([(p.timestamp - time_series_data[0].timestamp).days for p in time_series_data])
    
    # Simple linear fit
    if len(values) > 0:
        slope = np.polyfit(timestamps, values, 1)[0]
    else:
        slope = 0
    
    # Determine direction
    if abs(slope) < 0.001:
        direction = "stable"
    elif slope > 0:
        direction = "improving"
    else:
        direction = "declining"
    
    # Calculate rate (per week)
    rate_per_week = slope * 7
    
    # Confidence based on R-squared
    if len(values) > 2:
        correlation = np.corrcoef(timestamps, values)[0, 1]
        r_squared = correlation ** 2
        
        if r_squared > 0.7:
            confidence = "high"
        elif r_squared > 0.4:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "low"
    
    return {
        "direction": direction,
        "rate_per_week": round(rate_per_week, 4),
        "confidence": confidence,
        "interpretation": f"NDVI is {direction} at {abs(rate_per_week):.4f} per week"
    }


def save_temporal_data(
    farm_id: str,
    metric_type: str,
    value: float,
    is_anomaly: bool = False,
    anomaly_type: Optional[str] = None
) -> Dict:
    """
    Save temporal data point to database
    Args:
        farm_id: Farm identifier
        metric_type: Type of metric (NDVI, EVI, SAVI, etc.)
        value: Metric value
        is_anomaly: Whether this is an anomaly
        anomaly_type: Type of anomaly if applicable
    Returns:
        Saved record or error dict
    """
    try:
        supabase = get_supabase_client()
        
        data_point = {
            "farm_id": farm_id,
            "metric_type": metric_type.upper(),
            "value": value,
            "is_anomaly": is_anomaly,
            "anomaly_type": anomaly_type
        }
        
        result = supabase.table("temporal_data").insert(data_point).execute()
        
        if result.data:
            logger.info(f"✓ Saved temporal data: {metric_type}={value} for farm {farm_id}")
            return result.data[0]
        else:
            logger.warning("Temporal data save returned no data")
            return {"success": False, "error": "No data returned"}
            
    except Exception as e:
        logger.error(f"Failed to save temporal data: {e}")
        return {"success": False, "error": str(e)}

