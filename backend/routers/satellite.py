from fastapi import APIRouter

router = APIRouter()

@router.get("/satellite/test")
async def test_satellite():
    """Test endpoint for satellite router"""
    return {"message": "Satellite router working", "status": "ok"}
