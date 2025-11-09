from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from services.chat_service import (
    parse_farmer_query,
    build_context_for_llm,
    generate_response,
    save_chat,
    get_chat_history
)
from services.weather_service import get_current_weather
from services.temporal_service import get_historical_trend
from services.translation_service import translation_service, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    user_id: str
    farm_id: Optional[str] = None
    message: str
    include_context: bool = True
    language: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response_text: str
    response_text_native: Optional[str] = None
    detected_language: str
    suggestions: List[str]
    confidence_level: str
    intent: str
    entities: dict
    timestamp: str
    chat_id: str


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a chat message and get AI response
    Args:
        request: ChatRequest with user_id, farm_id, message
    Returns:
        ChatResponse with AI-generated answer and suggestions
    """
    try:
        logger.info(f"Chat request from user {request.user_id}: {request.message}")
        
        # Step 0: Handle translation if non-English
        original_message = request.message
        detected_language = "en"
        
        if request.language and request.language != "en":
            detected_language = request.language
            # Translate to English for processing
            request.message = translation_service.translate_to_english(request.message, detected_language)
            logger.info(f"Translated from {detected_language} to English")
        
        # Step 1: Parse query to understand intent
        parsed = parse_farmer_query(request.message)
        intent = parsed["intent"]
        entities = parsed["entities"]
        
        logger.info(f"Detected intent: {intent}, entities: {entities}")
        
        # Step 2: Build context if farm_id provided and context requested
        context = ""
        if request.farm_id and request.include_context:
            # Get latest analysis data (mock for now)
            latest_analysis = {
                "NDVI": 0.72,
                "EVI": 0.58,
                "SAVI": 0.65,
                "health_score": 75,
                "issues": [] if 0.72 > 0.6 else ["low_vegetation"]
            }
            
            # Get weather data if available
            weather_data = None
            if request.farm_id:
                # Mock coordinates - in production, get from farm metadata
                weather = get_current_weather(28.6139, 77.2090)
                if weather:
                    weather_data = {
                        "temperature": weather.temperature,
                        "humidity": weather.humidity,
                        "rainfall": weather.rainfall,
                        "description": weather.description
                    }
            
            # Get historical trends for health/diagnosis queries
            historical_trends = None
            if intent in ["health_check", "problem_diagnosis"]:
                trend_data = get_historical_trend(request.farm_id, "NDVI", days=30)
                if trend_data:
                    historical_trends = [
                        {"value": point.value, "date": point.timestamp}
                        for point in trend_data
                    ]
            
            context = build_context_for_llm(
                request.farm_id,
                intent,
                entities,
                latest_analysis,
                weather_data,
                historical_trends
            )
            
            logger.info(f"Built context ({len(context)} chars)")
        
        # Step 3: Generate response using LLM
        response = generate_response(
            request.message,
            context,
            intent,
            entities
        )
        
        logger.info(f"Generated response (source: {response.get('source')})")
        
        # Step 4: Save chat to database
        chat_record = save_chat(
            request.user_id,
            request.farm_id,
            request.message,
            response,
            intent,
            entities
        )
        
        # Step 5: Translate response back if needed
        response_text_native = None
        if detected_language != "en":
            response_text_native = translation_service.translate_from_english(
                response["response_text"], 
                detected_language
            )
            logger.info(f"Translated response back to {detected_language}")
        
        # Step 6: Return formatted response
        return ChatResponse(
            response_text=response["response_text"],
            response_text_native=response_text_native,
            detected_language=detected_language,
            suggestions=response["suggestions"],
            confidence_level=response["confidence_level"],
            intent=intent,
            entities=entities,
            timestamp=chat_record["timestamp"],
            chat_id=chat_record["id"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/chat/history/{farm_id}")
async def get_chat_history_endpoint(
    farm_id: str,
    limit: int = 50
):
    """
    Get chat history for a farm
    Args:
        farm_id: Farm identifier
        limit: Maximum number of messages to return
    Returns:
        Array of chat messages with timestamps
    """
    try:
        history = get_chat_history(farm_id, limit)
        
        return {
            "success": True,
            "farm_id": farm_id,
            "count": len(history),
            "messages": history
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/voice")
async def process_voice_message(
    user_id: str,
    farm_id: Optional[str] = None,
    # audio_file: UploadFile = File(...)  # Future implementation
):
    """
    Process voice message (future implementation)
    Will use Whisper API for transcription
    """
    return {
        "status": "not_implemented",
        "message": "Voice chat will be available in future update",
        "suggestion": "Please use text chat for now"
    }


@router.get("/chat/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }


@router.get("/chat/test")
async def test_chat():
    """Test endpoint for chat router"""
    return {"message": "Chat router working", "status": "ok"}
