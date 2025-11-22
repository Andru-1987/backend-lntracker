from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from services.trends_service import TrendsService

router = APIRouter()

@router.get("/trends_rss")
async def get_daily_trends():
    try:
        trends_data = TrendsService().get_trends_rss()
        
        return JSONResponse(
            content=trends_data,
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo tendencias diarias: {str(e)}",
        )