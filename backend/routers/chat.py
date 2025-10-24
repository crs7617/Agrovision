from fastapi import APIRouter

router = APIRouter()

@router.get("/chat/test")
async def test_chat():
    """Test endpoint for chat router"""
    return {"message": "Chat router working", "status": "ok"}
