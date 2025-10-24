from fastapi import APIRouter

router = APIRouter()

@router.get("/weather/test")
async def test_weather():
    """Test endpoint for weather router"""
    return {"message": "Weather router working", "status": "ok"}
