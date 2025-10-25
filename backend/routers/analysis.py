from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import numpy as np
from pathlib import Path
import json

from services.cv_service import FieldDetector
from services.segmentation_service import HealthZoneSegmenter

router = APIRouter()

# Initialize CV models (lazy loading)
field_detector = None
health_segmenter = None

def get_field_detector():
    """Lazy load field detector"""
    global field_detector
    if field_detector is None:
        field_detector = FieldDetector()
    return field_detector

def get_health_segmenter():
    """Lazy load health segmenter"""
    global health_segmenter
    if health_segmenter is None:
        health_segmenter = HealthZoneSegmenter()
    return health_segmenter


@router.get("/analysis/test")
async def test_analysis():
    """Test endpoint for analysis router"""
    return {"message": "Analysis router working", "status": "ok"}


@router.post("/detect-fields")
async def detect_fields(
    farm_id: Optional[str] = None,
    image_file: Optional[UploadFile] = File(None)
):
    """
    Detect field boundaries using YOLOv8
    
    Args:
        farm_id: Farm ID to load imagery from database
        image_file: Optional uploaded image file
    
    Returns:
        Detection results with bounding boxes
    """
    try:
        detector = get_field_detector()
        
        # For now, use dummy data (Phase 3 will load from database)
        if farm_id:
            # TODO: Load from database/fast_multispectral folder
            dummy_image = np.random.rand(4, 640, 640).astype(np.float32)
            image_array = dummy_image
        elif image_file:
            # TODO: Process uploaded file
            raise HTTPException(status_code=501, detail="File upload not yet implemented")
        else:
            raise HTTPException(status_code=400, detail="Provide either farm_id or image_file")
        
        # Run detection
        results = detector.detect_field_boundaries(image_array)
        
        if not results["success"]:
            raise HTTPException(status_code=500, detail=results.get("error", "Detection failed"))
        
        # Visualize (save to temp)
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        annotated_path = temp_dir / f"field_detection_{farm_id or 'upload'}.png"
        detector.visualize_detections(
            image_array,
            results["detections"],
            str(annotated_path)
        )
        
        return {
            "success": True,
            "farm_id": farm_id,
            "num_detections": results["num_detections"],
            "detections": results["detections"],
            "annotated_image_path": str(annotated_path),
            "message": f"Detected {results['num_detections']} field(s)"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.post("/segment-health")
async def segment_health(
    farm_id: str,
    analysis_id: Optional[str] = None
):
    """
    Segment crop health zones from NDVI data
    
    Args:
        farm_id: Farm identifier
        analysis_id: Optional analysis ID to load specific NDVI data
    
    Returns:
        Health zone statistics and mask URL
    """
    try:
        segmenter = get_health_segmenter()
        
        # For now, use dummy NDVI data (Phase 3 will load from database)
        # TODO: Load actual NDVI from database using farm_id/analysis_id
        ndvi_data = np.random.rand(512, 512).astype(np.float32)
        
        # Run segmentation
        results = segmenter.segment_health_zones(ndvi_data)
        
        if not results["success"]:
            raise HTTPException(status_code=500, detail=results.get("error", "Segmentation failed"))
        
        # Save visualization
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        mask_path = temp_dir / f"health_zones_{farm_id}_{analysis_id or 'latest'}.png"
        segmenter.save_mask_with_legend(
            results["mask"],
            str(mask_path),
            results["statistics"]
        )
        
        return {
            "success": True,
            "farm_id": farm_id,
            "analysis_id": analysis_id,
            "statistics": results["statistics"],
            "mask_url": str(mask_path),
            "message": "Health zones segmented successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation error: {str(e)}")


@router.get("/analysis/{analysis_id}/visualizations")
async def get_visualizations(analysis_id: str):
    """
    Retrieve all visualizations for an analysis
    
    Args:
        analysis_id: Analysis identifier
    
    Returns:
        Array of visualization URLs
    """
    try:
        temp_dir = Path("temp")
        
        # Find all visualizations for this analysis
        # TODO: In Phase 3, load from Supabase storage
        visualizations = []
        
        # Check for common visualization types
        viz_types = ["field_detection", "health_zones", "ndvi_heatmap"]
        
        for viz_type in viz_types:
            pattern = f"{viz_type}_{analysis_id}*.png"
            matching_files = list(temp_dir.glob(pattern))
            
            for file_path in matching_files:
                visualizations.append({
                    "type": viz_type,
                    "url": str(file_path),
                    "filename": file_path.name
                })
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "count": len(visualizations),
            "visualizations": visualizations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving visualizations: {str(e)}")


@router.get("/farms/{farm_id}/trends")
async def get_farm_trends(
    farm_id: str,
    index: str = "ndvi",
    days: int = 90
):
    """
    Get historical trends and anomaly detection for farm
    Args:
        farm_id: Farm identifier
        index: Spectral index to analyze (ndvi, evi, savi)
        days: Number of days to look back (default 90)
    Returns:
        Historical trends, anomalies, and seasonal comparison
    """
    from services.temporal_service import (
        get_historical_trend,
        detect_anomalies,
        calculate_trend_direction,
        compare_seasonal_pattern
    )
    
    try:
        # Get historical data
        time_series = get_historical_trend(farm_id, index.upper(), days)
        
        if not time_series:
            raise HTTPException(status_code=404, detail=f"No historical data found for farm {farm_id}")
        
        # Detect anomalies
        anomalies = detect_anomalies(time_series)
        
        # Calculate trend
        trend = calculate_trend_direction(time_series)
        
        # Get current values for seasonal comparison
        if time_series:
            current_value = time_series[-1].value
            current_data = {index.upper(): current_value}
            
            # Compare to seasonal baseline
            seasonal_comparison = compare_seasonal_pattern(
                current_data,
                farm_id,
                crop_type="wheat"  # TODO: Get from farm metadata
            )
        else:
            seasonal_comparison = {
                "comparison_text": "No data available",
                "is_normal": True,
                "deviation_percentage": 0
            }
        
        return {
            "success": True,
            "farm_id": farm_id,
            "index": index.upper(),
            "period_days": days,
            "data_points": len(time_series),
            "time_series": [point.to_dict() for point in time_series],
            "trend": trend,
            "anomalies": {
                "count": len(anomalies),
                "detected": [anomaly.to_dict() for anomaly in anomalies]
            },
            "seasonal_comparison": seasonal_comparison,
            "latest_value": time_series[-1].value if time_series else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")


# We'll add the full /analyze endpoint in Phase 3
