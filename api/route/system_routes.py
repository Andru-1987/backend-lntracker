from datetime import datetime
from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
async def health_check():

    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "Google News & Trends API (Modular)",
        "version": "2.0.0",
    }