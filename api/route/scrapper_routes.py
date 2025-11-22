from fastapi import APIRouter, HTTPException, Request
from utils.config import settings
import httpx
from models.models import DiariosRequest


router = APIRouter()

@router.post("/diarios")
async def proxy(payload: DiariosRequest):
    forward_client = settings.EXTERNAL_API_URL

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{forward_client}/scrape/codigo/{payload.codigo}"
            )

        response.raise_for_status()

        data = response.json()
        noticias = data.get("noticias", [])

        return {
            "status_code": response.status_code,
            "response": noticias
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo noticias: {str(e)}"
        )
