"""
LLM Interpretation Service using Groq (Free Tier)
Interprets spectral analysis data and generates farmer-friendly recommendations
"""
import os
import json
from typing import Dict, List, Optional
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Simple caching for responses
_response_cache = {}


def setup_llm_client():
    """
    Setup Groq client (free tier - no installation needed for now)
    We'll use HTTP requests to avoid heavy dependencies
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "":
        logger.warning("GROQ_API_KEY not set - LLM features will use fallback mode")
        return None
    
    # For Phase 3, we'll use requests library (already installed)
    return {"api_key": api_key, "endpoint": "https://api.groq.com/openai/v1/chat/completions"}


def call_groq_api(prompt: str, system_prompt: str, model: str = "llama-3.1-8b-instant") -> Optional[str]:
    """
    Call Groq API (free tier)
    Args:
        prompt: User prompt
        system_prompt: System instructions
        model: Model to use (llama-3.1-8b-instant is free)
    Returns:
        LLM response text or None if error
    """
    try:
        import requests
        
        client = setup_llm_client()
        if not client:
            return None
        
        headers = {
            "Authorization": f"Bearer {client['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(client["endpoint"], headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            logger.error(f"Groq API error: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None


def interpret_spectral_data(
    indices_dict: Dict[str, float],
    health_score: float,
    crop_type: str = "wheat"
) -> Dict:
    """
    Interpret spectral indices using LLM or rule-based fallback
    Args:
        indices_dict: Dictionary with NDVI, EVI, SAVI, etc.
        health_score: Overall health score (0-100)
        crop_type: Type of crop
    Returns:
        Dictionary with assessment, issues, and recommendations
    """
    # Create cache key
    cache_key = f"{crop_type}_{health_score:.2f}_{indices_dict.get('NDVI', 0):.2f}"
    
    if cache_key in _response_cache:
        logger.info("Using cached LLM response")
        return _response_cache[cache_key]
    
    # Build prompt
    ndvi = indices_dict.get("NDVI", 0)
    evi = indices_dict.get("EVI", 0)
    savi = indices_dict.get("SAVI", 0)
    ndwi = indices_dict.get("NDWI", 0)
    
    system_prompt = """You are an expert agricultural advisor with 20 years of experience in crop health analysis using satellite imagery. 
Your job is to interpret vegetation indices and provide actionable advice to farmers in simple, clear language.
Focus on practical recommendations that farmers can implement."""
    
    user_prompt = f"""Analyze this {crop_type} crop health data:

- NDVI (Vegetation Health): {ndvi:.3f}
- EVI (Enhanced Vegetation): {evi:.3f}
- SAVI (Soil-Adjusted Vegetation): {savi:.3f}
- NDWI (Water Content): {ndwi:.3f}
- Overall Health Score: {health_score:.1f}/100

Provide:
1. Health Assessment (1 sentence)
2. Likely Issues (2-3 bullet points)
3. Recommendations (3-4 specific actions)

Keep it simple and farmer-friendly."""
    
    # Try LLM first
    llm_response = call_groq_api(user_prompt, system_prompt)
    
    if llm_response:
        # Parse LLM response
        result = {
            "assessment_text": llm_response.split('\n')[0] if llm_response else "Analysis complete",
            "issues_list": [line.strip('- ').strip() for line in llm_response.split('\n') if line.strip().startswith('-')][:3],
            "recommendations_list": [line.strip('- ').strip() for line in llm_response.split('\n') if line.strip().startswith('-')][3:],
            "source": "llm"
        }
    else:
        # Fallback to rule-based interpretation
        result = _fallback_interpretation(indices_dict, health_score, crop_type)
    
    # Cache the response
    _response_cache[cache_key] = result
    
    return result


def _fallback_interpretation(indices_dict: Dict, health_score: float, crop_type: str) -> Dict:
    """
    Rule-based fallback when LLM is unavailable
    """
    ndvi = indices_dict.get("NDVI", 0)
    ndwi = indices_dict.get("NDWI", 0)
    
    issues = []
    recommendations = []
    
    # Assessment based on health score
    if health_score >= 75:
        assessment = f"Your {crop_type} crop is in excellent health with strong vegetation growth."
    elif health_score >= 60:
        assessment = f"Your {crop_type} crop is in good condition with minor areas needing attention."
    elif health_score >= 40:
        assessment = f"Your {crop_type} crop shows moderate stress and requires intervention."
    else:
        assessment = f"Your {crop_type} crop is under severe stress and needs immediate action."
    
    # Identify issues
    if ndvi < 0.5:
        issues.append("Low vegetation density detected - possible nutrient deficiency")
    if ndwi < -0.1:
        issues.append("Water stress detected - soil moisture is low")
    if ndvi > 0.5 and health_score < 60:
        issues.append("Possible pest or disease affecting crop health")
    
    if not issues:
        issues.append("No major issues detected - continue regular monitoring")
    
    # Generate recommendations
    if ndwi < -0.1:
        recommendations.append("Increase irrigation frequency to address water stress")
    if ndvi < 0.5:
        recommendations.append("Apply nitrogen-rich fertilizer to boost growth")
        recommendations.append("Conduct soil testing to check nutrient levels")
    recommendations.append(f"Monitor crop every 7 days for changes")
    
    return {
        "assessment_text": assessment,
        "issues_list": issues[:3],
        "recommendations_list": recommendations[:4],
        "source": "rule_based"
    }


def generate_farmer_response(
    query: str,
    context: Dict,
    max_length: int = 300
) -> str:
    """
    Generate conversational response to farmer queries
    Args:
        query: Farmer's question
        context: Dictionary with farm data, analysis, trends
        max_length: Maximum response length
    Returns:
        Plain text response in simple language
    """
    # Extract context
    farm_name = context.get("farm_name", "your farm")
    crop_type = context.get("crop_type", "crop")
    health_score = context.get("health_score", 50)
    ndvi = context.get("ndvi", 0.5)
    
    system_prompt = """You are a helpful agricultural assistant talking to farmers in India. 
Use simple language, avoid technical jargon, and provide practical advice.
Use metric units (hectares, kilograms, liters).
Be encouraging and supportive."""
    
    user_prompt = f"""Farm: {farm_name}
Crop: {crop_type}
Current Health: {health_score}/100 (NDVI: {ndvi:.2f})

Farmer asks: {query}

Provide a helpful, friendly response (max 2-3 sentences)."""
    
    # Try LLM
    llm_response = call_groq_api(user_prompt, system_prompt)
    
    if llm_response:
        # Truncate if too long
        if len(llm_response) > max_length:
            llm_response = llm_response[:max_length] + "..."
        return llm_response
    
    # Fallback response
    return f"Based on the latest analysis of {farm_name}, your {crop_type} has a health score of {health_score}/100. I recommend checking the detailed recommendations in your dashboard for specific actions to improve crop health."


def clear_response_cache():
    """Clear the LLM response cache"""
    global _response_cache
    _response_cache = {}
    logger.info("LLM response cache cleared")
