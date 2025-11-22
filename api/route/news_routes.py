from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
from utils.config import settings

router = APIRouter()


@router.get("/news")
async def get_news(codigo: str = "06"):
    forward_client = settings.EXTERNAL_API_URL

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{forward_client}/scrape/codigo/{codigo}")

        # Verifica status HTTP
        response.raise_for_status()

        # Decodificar JSON
        data = response.json()

        noticias = data.get("noticias", [])

        return JSONResponse(
            content={"google_news": noticias},
            status_code=200
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo noticias: {str(e)}"
        )
