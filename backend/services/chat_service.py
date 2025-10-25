"""
Chat Service with Conversational Logic
Handles farmer queries with context awareness and LLM integration
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from services.llm_service import call_groq_api, setup_llm_client
from services.knowledge_base import get_crop_info, diagnose_issue, recommend_actions

logger = logging.getLogger(__name__)

# Intent patterns for query classification
INTENT_PATTERNS = {
    "health_check": [
        r"how.*crop.*doing",
        r"health.*farm",
        r"crop.*healthy",
        r"how.*field.*looking",
        r"status.*crop",
        r"check.*health"
    ],
    "recommendation": [
        r"what.*should.*do",
        r"recommend",
        r"suggest",
        r"advice",
        r"next.*step",
        r"how.*improve",
        r"what.*fertilizer",
        r"which.*pesticide",
        r"best.*practice"
    ],
    "problem_diagnosis": [
        r"problem",
        r"issue",
        r"wrong",
        r"yellowing",
        r"dying",
        r"disease",
        r"pest",
        r"damage",
        r"stress",
        r"plants.*turning",
        r"leaves.*yellow",
        r"crop.*sick"
    ],
    "general_info": [
        r"what.*is",
        r"explain",
        r"tell.*about",
        r"information",
        r"learn.*about"
    ],
    "weather": [
        r"weather",
        r"rain",
        r"temperature",
        r"forecast",
        r"climate"
    ]
}

# Crop type patterns
CROP_PATTERNS = {
    "wheat": r"\b(wheat|gehun)\b",
    "rice": r"\b(rice|dhan|paddy)\b",
    "corn": r"\b(corn|maize|makka)\b",
    "cotton": r"\b(cotton|kapas)\b"
}


def parse_farmer_query(message: str) -> Dict:
    """
    Extract intent and entities from farmer's message
    Args:
        message: Farmer's query text
    Returns:
        Dictionary with intent, entities, and confidence
    """
    message_lower = message.lower()
    
    # Detect intent
    detected_intent = "general_info"  # Default
    max_matches = 0
    
    for intent, patterns in INTENT_PATTERNS.items():
        matches = sum(1 for pattern in patterns if re.search(pattern, message_lower))
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent
    
    # Extract entities
    entities = {}
    
    # Extract crop type
    for crop, pattern in CROP_PATTERNS.items():
        if re.search(pattern, message_lower):
            entities["crop_type"] = crop
            break
    
    # Extract date references (today, yesterday, last week, etc.)
    date_entity = None
    if re.search(r"\btoday\b", message_lower):
        date_entity = datetime.now().strftime("%Y-%m-%d")
    elif re.search(r"\byesterday\b", message_lower):
        date_entity = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif re.search(r"\blast\s+week\b", message_lower):
        date_entity = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    if date_entity:
        entities["date"] = date_entity
    
    # Extract farm name (simple pattern - looks for "Farm X" or "field X")
    farm_match = re.search(r"(?:farm|field)\s+(\w+)", message_lower)
    if farm_match:
        entities["farm_name"] = farm_match.group(1)
    
    # Calculate confidence
    confidence = "high" if max_matches >= 2 else "medium" if max_matches == 1 else "low"
    
    logger.info(f"Parsed query - Intent: {detected_intent}, Entities: {entities}, Confidence: {confidence}")
    
    return {
        "intent": detected_intent,
        "entities": entities,
        "confidence": confidence,
        "original_message": message
    }


def build_context_for_llm(
    farm_id: str,
    intent: str,
    entities: Dict,
    latest_analysis: Optional[Dict] = None,
    weather_data: Optional[Dict] = None,
    historical_trends: Optional[List] = None
) -> str:
    """
    Build context string for LLM with relevant farm data
    Args:
        farm_id: Farm identifier
        intent: Detected intent
        entities: Extracted entities
        latest_analysis: Most recent satellite analysis data
        weather_data: Current weather information
        historical_trends: Historical NDVI/health trends
    Returns:
        Formatted context string for LLM
    """
    context_parts = []
    
    # Add farm identification
    context_parts.append(f"Farm ID: {farm_id}")
    
    if entities.get("crop_type"):
        crop_info = get_crop_info(entities["crop_type"])
        context_parts.append(f"Crop Type: {entities['crop_type']}")
        context_parts.append(f"Optimal NDVI Range: {crop_info['optimal_ndvi']}")
        context_parts.append(f"Water Needs: {crop_info['water_needs']}")
    
    # Add latest satellite analysis
    if latest_analysis:
        context_parts.append("\n--- Latest Crop Health Analysis ---")
        context_parts.append(f"NDVI: {latest_analysis.get('NDVI', 'N/A')}")
        context_parts.append(f"EVI: {latest_analysis.get('EVI', 'N/A')}")
        context_parts.append(f"Health Score: {latest_analysis.get('health_score', 'N/A')}/100")
        
        if latest_analysis.get('issues'):
            context_parts.append(f"Detected Issues: {', '.join(latest_analysis['issues'])}")
    
    # Add weather context
    if weather_data:
        context_parts.append("\n--- Current Weather Conditions ---")
        context_parts.append(f"Temperature: {weather_data.get('temperature', 'N/A')}°C")
        context_parts.append(f"Humidity: {weather_data.get('humidity', 'N/A')}%")
        context_parts.append(f"Recent Rainfall: {weather_data.get('rainfall', 'N/A')}mm")
        
        if weather_data.get('description'):
            context_parts.append(f"Weather: {weather_data['description']}")
        
        if weather_data.get('forecast'):
            context_parts.append(f"7-Day Outlook: {weather_data['forecast']}")
    
    # Add historical trends for trend-based queries
    if historical_trends and intent in ["health_check", "problem_diagnosis"]:
        context_parts.append("\n--- Historical Trend ---")
        if len(historical_trends) >= 2:
            recent_values = [point.get('value', 0) for point in historical_trends[-5:]]
            trend_direction = "improving" if recent_values[-1] > recent_values[0] else "declining"
            context_parts.append(f"Recent Trend: {trend_direction}")
            context_parts.append(f"Last 5 readings: {[f'{v:.2f}' for v in recent_values]}")
    
    # Add intent-specific context
    if intent == "problem_diagnosis" and latest_analysis:
        diagnosis = diagnose_issue(
            latest_analysis,
            entities.get("crop_type", "wheat")
        )
        context_parts.append("\n--- Diagnosis ---")
        context_parts.append(f"Confidence: {diagnosis.get('confidence', 0)}")
        for issue in diagnosis.get('issues', []):
            context_parts.append(f"- {issue.get('description', 'Unknown issue')}")
    
    return "\n".join(context_parts)


def generate_response(
    query: str,
    context: str,
    intent: str,
    entities: Dict
) -> Dict:
    """
    Generate conversational response using LLM
    Args:
        query: Farmer's original question
        context: Built context with farm/weather/analysis data
        intent: Detected intent
        entities: Extracted entities
    Returns:
        Dictionary with response_text, suggestions, and confidence_level
    """
    # Build system prompt for agricultural expert
    system_prompt = """You are an experienced agricultural advisor helping Indian farmers.
Your role is to provide practical, actionable advice in simple language.

Guidelines:
- Be conversational and friendly
- Avoid technical jargon unless necessary
- Provide specific, actionable recommendations
- Include cost estimates in Indian Rupees when relevant
- Consider local farming practices
- Be encouraging and supportive
- If data is limited, acknowledge it but still provide helpful guidance
- Keep responses concise (2-3 paragraphs max)
"""
    
    # Build user prompt with context and query
    user_prompt = f"""Farmer's Question: {query}

Farm Context:
{context}

Please provide a helpful response that:
1. Directly answers their question
2. Explains any relevant data points in simple terms
3. Gives 2-3 specific action items if applicable
4. Suggests follow-up steps or monitoring points

Keep it conversational and practical."""
    
    # Check if LLM is available
    llm_client = setup_llm_client()
    
    if llm_client:
        try:
            # Call LLM
            llm_response = call_groq_api(user_prompt, system_prompt)
            
            if llm_response:
                # Extract suggestions from response
                suggestions = _extract_suggestions(llm_response)
                
                return {
                    "response_text": llm_response,
                    "suggestions": suggestions,
                    "confidence_level": "high",
                    "source": "llm"
                }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
    
    # Fallback: Rule-based response
    logger.info("Using rule-based response generation")
    return _generate_rule_based_response(query, context, intent, entities)


def _extract_suggestions(response_text: str) -> List[str]:
    """Extract actionable suggestions from LLM response"""
    suggestions = []
    
    # Look for numbered lists or bullet points
    lines = response_text.split('\n')
    for line in lines:
        # Match patterns like "1.", "2.", "-", "*"
        if re.match(r'^\s*[\d\-\*•]\s*[\.)]?\s*', line):
            suggestion = re.sub(r'^\s*[\d\-\*•]\s*[\.)]?\s*', '', line).strip()
            if len(suggestion) > 10:  # Filter out very short items
                suggestions.append(suggestion)
    
    # Limit to top 5 suggestions
    return suggestions[:5]


def _generate_rule_based_response(
    query: str,
    context: str,
    intent: str,
    entities: Dict
) -> Dict:
    """Generate response using rule-based logic (fallback)"""
    
    suggestions = []
    
    if intent == "health_check":
        response_text = f"Based on the latest analysis of your farm, "
        
        # Try to extract health score from context
        health_match = re.search(r"Health Score: (\d+)/100", context)
        if health_match:
            score = int(health_match.group(1))
            if score >= 75:
                response_text += f"your crop is in good health (score: {score}/100). Keep up the regular monitoring and maintenance."
                suggestions = [
                    "Continue regular irrigation schedule",
                    "Monitor for any pest activity",
                    "Check weather forecast for next week"
                ]
            elif score >= 50:
                response_text += f"your crop shows moderate health (score: {score}/100). Some attention is needed."
                suggestions = [
                    "Investigate areas with lower NDVI values",
                    "Check soil moisture levels",
                    "Consider nutrient supplementation"
                ]
            else:
                response_text += f"your crop needs immediate attention (score: {score}/100)."
                suggestions = [
                    "Conduct soil and water tests",
                    "Consult with local agricultural officer",
                    "Check for pest or disease signs"
                ]
        else:
            response_text += "I don't have recent analysis data. I recommend scheduling a new satellite scan."
            suggestions = ["Request new satellite analysis", "Check field manually"]
    
    elif intent == "recommendation":
        response_text = "Based on your farm's current condition, here are my recommendations: "
        
        # Extract issues from context
        if "Detected Issues:" in context:
            response_text += "I see there are some issues detected. "
            suggestions = [
                "Review detailed analysis report",
                "Prioritize high-severity issues first",
                "Monitor changes over next 7 days"
            ]
        else:
            response_text += "Your farm appears stable. Continue with regular care practices."
            suggestions = [
                "Maintain current irrigation schedule",
                "Plan for upcoming season",
                "Keep monitoring weekly"
            ]
    
    elif intent == "problem_diagnosis":
        response_text = "Let me help you diagnose the issue. "
        
        if "yellowing" in query.lower():
            response_text += "Yellowing leaves often indicate nitrogen deficiency or water stress. "
            suggestions = [
                "Apply nitrogen-based fertilizer (Urea 20-30 kg/acre)",
                "Check irrigation - ensure adequate water",
                "Test soil for nutrient levels (₹500-1000)"
            ]
        elif "dying" in query.lower():
            response_text += "This is concerning and needs immediate attention. "
            suggestions = [
                "Inspect plants closely for pests/disease",
                "Check soil moisture immediately",
                "Contact local agricultural extension officer"
            ]
        else:
            response_text += "Based on available data, I recommend conducting a detailed field inspection."
            suggestions = [
                "Check for visible signs of pests or disease",
                "Test soil and water quality",
                "Review recent weather impact"
            ]
    
    elif intent == "weather":
        response_text = "Let me provide weather information. "
        
        if "Temperature:" in context:
            temp_match = re.search(r"Temperature: ([\d.]+)", context)
            if temp_match:
                temp = float(temp_match.group(1))
                response_text += f"Current temperature is {temp}°C. "
                
                if temp > 35:
                    response_text += "High temperature detected - ensure adequate irrigation."
                    suggestions = ["Increase irrigation frequency", "Monitor for heat stress"]
                else:
                    response_text += "Temperature is within normal range."
                    suggestions = ["Continue regular care"]
        else:
            response_text += "Weather data is currently unavailable. Please check back later."
            suggestions = ["Monitor local weather manually"]
    
    else:  # general_info
        crop_type = entities.get("crop_type", "crop")
        response_text = f"I'm here to help you with {crop_type} farming. "
        response_text += "You can ask me about crop health, weather impact, recommendations, or any problems you're facing."
        suggestions = [
            "Ask about current crop health",
            "Get weather forecast",
            "Request recommendations"
        ]
    
    return {
        "response_text": response_text,
        "suggestions": suggestions if suggestions else ["Ask another question", "Request detailed analysis"],
        "confidence_level": "medium",
        "source": "rule_based"
    }


def save_chat(
    user_id: str,
    farm_id: Optional[str],
    message: str,
    response: Dict,
    intent: str,
    entities: Dict
) -> Dict:
    """
    Save chat conversation to database
    Args:
        user_id: User identifier
        farm_id: Farm identifier (optional)
        message: User's message
        response: Generated response dictionary
        intent: Detected intent
        entities: Extracted entities
    Returns:
        Saved chat record with ID and timestamp
    """
    # For Phase 5, we'll use in-memory storage
    # In production, this would save to Supabase chat_history table
    
    chat_record = {
        "id": f"chat_{user_id}_{int(datetime.now().timestamp())}",
        "user_id": user_id,
        "farm_id": farm_id,
        "message": message,
        "response_text": response.get("response_text"),
        "suggestions": response.get("suggestions", []),
        "intent": intent,
        "entities": entities,
        "confidence": response.get("confidence_level"),
        "timestamp": datetime.now().isoformat(),
        "source": response.get("source", "unknown")
    }
    
    logger.info(f"Chat saved: {chat_record['id']} for user {user_id}")
    
    # TODO: Save to Supabase
    # supabase.table("chat_history").insert(chat_record).execute()
    
    return chat_record


def get_chat_history(
    farm_id: str,
    limit: int = 50
) -> List[Dict]:
    """
    Retrieve chat history for a farm
    Args:
        farm_id: Farm identifier
        limit: Maximum number of records
    Returns:
        List of chat records
    """
    # For Phase 5, return mock data
    # In production, query Supabase
    
    logger.info(f"Retrieving chat history for farm {farm_id}")
    
    # TODO: Query from Supabase
    # result = supabase.table("chat_history").select("*").eq("farm_id", farm_id).limit(limit).execute()
    # return result.data
    
    # Mock response
    return [
        {
            "id": f"chat_{farm_id}_001",
            "message": "How is my wheat crop doing?",
            "response_text": "Your wheat crop is in good health with NDVI of 0.72",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "id": f"chat_{farm_id}_002",
            "message": "What should I do about yellowing leaves?",
            "response_text": "Yellowing may indicate nitrogen deficiency. Apply urea fertilizer.",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
