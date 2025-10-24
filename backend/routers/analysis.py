from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()

@router.get("/analysis/test")
async def test_analysis():
    """Test endpoint for analysis router"""
    return {"message": "Analysis router working", "status": "ok"}

# We'll add the full /analyze endpoint in Phase 3
