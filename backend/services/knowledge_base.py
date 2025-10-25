"""
Agricultural Knowledge Base
Crop-specific thresholds, diseases, and recommendations
"""
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


# Crop-specific optimal ranges and characteristics
CROPS_KNOWLEDGE = {
    "wheat": {
        "optimal_ndvi": (0.6, 0.8),
        "optimal_evi": (0.4, 0.6),
        "optimal_savi": (0.5, 0.7),
        "water_needs": "moderate",  # mm/week
        "growth_stages": {
            "tillering": {"ndvi": 0.3, "days": 30},
            "jointing": {"ndvi": 0.6, "days": 60},
            "heading": {"ndvi": 0.75, "days": 90},
            "maturity": {"ndvi": 0.5, "days": 120}
        },
        "common_issues": {
            "yellow_rust": "Low NDVI with patchy patterns",
            "water_stress": "NDVI < 0.5, NDWI < -0.1",
            "nitrogen_deficiency": "NDVI < 0.5, uniform pattern"
        }
    },
    "rice": {
        "optimal_ndvi": (0.7, 0.85),
        "optimal_evi": (0.5, 0.7),
        "optimal_savi": (0.6, 0.8),
        "water_needs": "high",
        "growth_stages": {
            "transplanting": {"ndvi": 0.2, "days": 10},
            "tillering": {"ndvi": 0.5, "days": 30},
            "panicle": {"ndvi": 0.8, "days": 60},
            "maturity": {"ndvi": 0.6, "days": 120}
        },
        "common_issues": {
            "blast_disease": "Sudden NDVI drop, localized",
            "water_stress": "NDVI < 0.6, NDWI < 0.0",
            "nutrient_deficiency": "NDVI < 0.6, yellowing"
        }
    },
    "corn": {
        "optimal_ndvi": (0.65, 0.85),
        "optimal_evi": (0.45, 0.65),
        "optimal_savi": (0.55, 0.75),
        "water_needs": "high",
        "growth_stages": {
            "emergence": {"ndvi": 0.3, "days": 14},
            "vegetative": {"ndvi": 0.7, "days": 45},
            "tasseling": {"ndvi": 0.85, "days": 70},
            "maturity": {"ndvi": 0.5, "days": 120}
        },
        "common_issues": {
            "drought_stress": "NDVI < 0.6, NDWI < -0.15",
            "nitrogen_deficiency": "NDVI < 0.55, lower leaves yellow",
            "disease": "Irregular NDVI patterns"
        }
    },
    "cotton": {
        "optimal_ndvi": (0.6, 0.75),
        "optimal_evi": (0.4, 0.6),
        "optimal_savi": (0.5, 0.7),
        "water_needs": "moderate",
        "growth_stages": {
            "seedling": {"ndvi": 0.3, "days": 21},
            "squaring": {"ndvi": 0.6, "days": 50},
            "flowering": {"ndvi": 0.7, "days": 80},
            "boll": {"ndvi": 0.65, "days": 120}
        },
        "common_issues": {
            "water_stress": "NDVI < 0.5, leaf curling",
            "pest_damage": "Patchy low NDVI",
            "nutrient_stress": "Uniform low NDVI < 0.55"
        }
    },
    "default": {
        "optimal_ndvi": (0.6, 0.8),
        "optimal_evi": (0.4, 0.6),
        "optimal_savi": (0.5, 0.7),
        "water_needs": "moderate",
        "growth_stages": {},
        "common_issues": {
            "general_stress": "Low vegetation indices"
        }
    }
}


def get_crop_info(crop_type: str) -> Dict:
    """
    Get knowledge base entry for crop type
    Args:
        crop_type: Type of crop
    Returns:
        Dictionary with crop-specific information
    """
    crop_type_lower = crop_type.lower()
    return CROPS_KNOWLEDGE.get(crop_type_lower, CROPS_KNOWLEDGE["default"])


def diagnose_issue(indices: Dict[str, float], crop_type: str) -> Dict:
    """
    Diagnose crop health issues based on spectral indices
    Args:
        indices: Dictionary of spectral indices (NDVI, EVI, SAVI, NDWI, etc.)
        crop_type: Type of crop being analyzed
    Returns:
        Diagnosis with confidence score and issues list
    """
    crop_info = get_crop_info(crop_type)
    issues = []
    confidence_scores = []
    
    ndvi = indices.get("NDVI", 0.5)
    evi = indices.get("EVI", 0.3)
    savi = indices.get("SAVI", 0.4)
    ndwi = indices.get("NDWI", 0.0)
    
    # Check NDVI range
    ndvi_min, ndvi_max = crop_info["optimal_ndvi"]
    if ndvi < ndvi_min:
        severity = "severe" if ndvi < ndvi_min * 0.7 else "moderate"
        issues.append({
            "type": "low_vegetation_health",
            "severity": severity,
            "description": f"NDVI ({ndvi:.2f}) is below optimal range ({ndvi_min}-{ndvi_max})",
            "confidence": 0.9
        })
        confidence_scores.append(0.9)
    elif ndvi > ndvi_max:
        issues.append({
            "type": "excessive_vegetation",
            "severity": "low",
            "description": f"NDVI ({ndvi:.2f}) is above typical range - may indicate dense growth",
            "confidence": 0.6
        })
        confidence_scores.append(0.6)
    
    # Check water stress (NDWI)
    if ndwi < -0.1:
        severity = "severe" if ndwi < -0.2 else "moderate"
        issues.append({
            "type": "water_stress",
            "severity": severity,
            "description": f"NDWI ({ndwi:.2f}) indicates water stress",
            "confidence": 0.85
        })
        confidence_scores.append(0.85)
    
    # Check if healthy
    if not issues:
        issues.append({
            "type": "healthy",
            "severity": "none",
            "description": f"All indices within optimal range for {crop_type}",
            "confidence": 0.95
        })
        confidence_scores.append(0.95)
    
    # Overall confidence
    overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
    
    return {
        "diagnosis": "healthy" if not any(i["type"] != "healthy" for i in issues) else "stressed",
        "issues": issues,
        "confidence": overall_confidence,
        "crop_info": crop_info
    }


def recommend_actions(
    diagnosis: Dict,
    weather_data: Dict = None,
    farm_area: float = 1.0
) -> List[Dict]:
    """
    Generate specific recommendations based on diagnosis
    Args:
        diagnosis: Output from diagnose_issue()
        weather_data: Optional weather forecast
        farm_area: Farm area in hectares
    Returns:
        List of prioritized recommendations
    """
    recommendations = []
    issues = diagnosis.get("issues", [])
    
    # Check for rain in forecast
    rain_expected = False
    if weather_data:
        rain_expected = weather_data.get("rain_forecast_7days", 0) > 10  # mm
    
    for issue in issues:
        issue_type = issue["type"]
        severity = issue["severity"]
        
        if issue_type == "water_stress" and severity in ["moderate", "severe"]:
            if rain_expected:
                rec = {
                    "action": "Monitor irrigation - rain expected",
                    "priority": "medium",
                    "timeframe": "this_week",
                    "details": "Rain is forecasted. Monitor soil moisture before irrigating.",
                    "estimated_cost": "₹0"
                }
            else:
                irrigation_amount = 25 if severity == "moderate" else 40  # mm
                rec = {
                    "action": f"Immediate irrigation needed",
                    "priority": "high" if severity == "severe" else "medium",
                    "timeframe": "immediate",
                    "details": f"Apply {irrigation_amount}mm of water (~{int(irrigation_amount * farm_area * 10)}L for {farm_area} hectare)",
                    "estimated_cost": f"₹{int(irrigation_amount * farm_area * 50)}"
                }
            recommendations.append(rec)
        
        elif issue_type == "low_vegetation_health":
            recommendations.append({
                "action": "Soil testing and nutrient analysis",
                "priority": "high",
                "timeframe": "this_week",
                "details": "Low NDVI may indicate nutrient deficiency. Test soil for N-P-K levels.",
                "estimated_cost": f"₹{int(500 * farm_area)}"
            })
            
            recommendations.append({
                "action": "Apply nitrogen fertilizer",
                "priority": "medium",
                "timeframe": "after_soil_test",
                "details": "Based on soil test, apply urea or DAP as needed",
                "estimated_cost": f"₹{int(2000 * farm_area)}"
            })
        
        elif issue_type == "healthy":
            recommendations.append({
                "action": "Continue current management",
                "priority": "low",
                "timeframe": "ongoing",
                "details": "Crop health is good. Maintain current irrigation and fertilization schedule.",
                "estimated_cost": "₹0"
            })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    return recommendations


def get_health_category(ndvi: float, crop_type: str = "default") -> Tuple[str, str]:
    """
    Categorize crop health based on NDVI
    Args:
        ndvi: NDVI value
        crop_type: Type of crop
    Returns:
        Tuple of (category, description)
    """
    crop_info = get_crop_info(crop_type)
    optimal_min, optimal_max = crop_info["optimal_ndvi"]
    
    if ndvi >= optimal_max:
        return "excellent", "Vegetation is thriving with optimal growth"
    elif ndvi >= optimal_min:
        return "good", "Vegetation health is within normal range"
    elif ndvi >= optimal_min * 0.7:
        return "fair", "Vegetation shows signs of stress, requires attention"
    else:
        return "poor", "Vegetation is severely stressed, immediate action needed"
