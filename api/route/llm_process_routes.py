import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from models.llm_model_request import PromptRequest
from llm.gemini_responses import analizar_noticias

from utils.key_builder import request_key_builder
from utils.config import settings
from utils.db_check_cnx import ensure_db_connection
from services.trends_service import TrendsService
from services.db_service_data import NewsWareHouseData
from fastapi_cache.decorator import cache


router = APIRouter()

@router.post("/recomendacion_benchmark")
@cache(expire=3600, key_builder=request_key_builder)
async def get_prompt_result(prompt_request: PromptRequest, request: Request) -> JSONResponse:
    
    forward_client = settings.EXTERNAL_API_URL
    competencia_titulos = []
    lanacion_titulos = []

    # 1. OBTENCIÓN DE DATOS DE LA COMPETENCIA

    if prompt_request.competencia in ("Google Trends", "google_trends"):
        try:
            trends_data = TrendsService().get_trends_rss()
            # Asumiendo que trends_data devuelve un dict donde los values son listas de artículos
            for _, articles in trends_data.items():
                competencia_titulos.extend([article['title'] for article in articles])
        except Exception as e:
            print(f"Error obteniendo Trends: {e}")

    else:
        # Scrape de competencia vía API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{forward_client}/scrape/codigo/{prompt_request.competencia_code}/cache"
                )
                response.raise_for_status() # Lanza error si no es 200
                data_comp = response.json()
                competencia_titulos = [noticia["titulo"] for noticia in data_comp.get("noticias", [])]

        except Exception as e:
            print(f"Error obteniendo competencia API: {e}")

    # 2. OBTENCIÓN DE DATOS PROPIOS (LA NACIÓN) CON FALLBACK
    
    try:
        print("Intentando obtener noticias desde SQL Server...")
        await ensure_db_connection(request)
        retriever = NewsWareHouseData(request.app.state.mssql)
        lanacion_titulos = retriever.get_all_news_category_list(prompt_request.categoria)
        
    except Exception as e:
        # Intento B: Fallback a API (Scraper/Cache)
        print(f"Fallo SQL ({e}). Usando Fallback API para La Nación...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{forward_client}/scrape/codigo/01/cache" 
                )
                response.raise_for_status()
                ln_data_json = response.json()
                lanacion_titulos = [noticia["titulo"] for noticia in ln_data_json.get("noticias", [])]

        except Exception as api_error:
            return JSONResponse(
                content={"error": "No se pudieron obtener las noticias de origen (ni SQL ni API)."}, 
                status_code=500
            )

    # 3. ANÁLISIS CON IA (VERTEX AI)
    
    try:
        ia_output = analizar_noticias(
            lanacion_titulos=lanacion_titulos,
            competencia_titulos=competencia_titulos,
            categoria=prompt_request.categoria
        )

        return JSONResponse(
            content=ia_output,
            status_code=200,
            media_type="application/json"
        )
        
    except Exception as e:
        return JSONResponse(
            content={"detail": f"Error durante el análisis de IA: {str(e)}"},
            status_code=500
        )
