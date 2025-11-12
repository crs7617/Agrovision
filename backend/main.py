from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

from models.schemas import HealthCheckResponse
from routers import analysis, satellite, chat, weather, farms

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AgroVision AI API",
    description="Agricultural Intelligence Platform Backend",
    version="1.0.0"
)

# CORS Configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3001"),
        "https://agrovision-zeta.vercel.app",
        "http://localhost:3001",
        "http://localhost:3000"  # Fallback for both ports
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now()
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AgroVision AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(farms.router, prefix="/api", tags=["Farms"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(satellite.router, prefix="/api", tags=["Satellite"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(weather.router, prefix="/api", tags=["Weather"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
