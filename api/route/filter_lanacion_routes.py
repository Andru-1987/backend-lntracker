from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, List

import httpx

from utils.config import settings
from utils.db_check_cnx import ensure_db_connection
from services.db_service_data import NewsWareHouseData

router = APIRouter()

@router.get("/categories")
async def categories(request:Request) -> JSONResponse:
    await ensure_db_connection(request)


    try:
        retriever = NewsWareHouseData(request.app.state.mssql)

        data ={}
        from_msserver = retriever.get_all_categories()


        data["data"] = from_msserver
        data["total"] = len(from_msserver)


        return JSONResponse(
            content=data,
            status_code=200,
            media_type="application/json"
            )
    
    except Exception as e:
        # fallback
        data = {}

        categories = ["agencias",
        "deportes",
        "economia",
        "el-mundo",
        "espectaculos",
        "estados-unidos",
        "ideas",
        "juegos",
        "lifestyle",
        "politica",
        "propiedades",
        "revista-hola",
        "revista-jardin",
        "revista-lugares",
        "salud",
        "seguridad",
        "sociedad"]
        data["data"] = categories
        data["total"]=len(categories)

        return JSONResponse(
            content=data,
            status_code=200,
            media_type="application/json"
        )



@router.get("/all_noticias_by_categories")
async def obtener_noticias_por_categoria(request:Request) -> JSONResponse:
    
    await ensure_db_connection(request)
    
    try:
        retriever = NewsWareHouseData(request.app.state.mssql)

        data ={}
        from_msserver = retriever.get_all_news_json()


        data["data"] = from_msserver

        for categoria, items in from_msserver.items():
            data[f"total_by_{categoria}"] = len(items)

        return JSONResponse(
            content=data,
            status_code=200,
            media_type="application/json"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener noticias: {str(e)}")


@router.get("/benchmarkNews")
async def obtener_competencias() -> JSONResponse:
    forward_client = settings.EXTERNAL_API_URL

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{forward_client}/medios/codigos")

        # Ver errores
        response.raise_for_status()

        data = response.json()
        medios = data.get("medios", {})

        # Filtrar lanacion
        medios_filtrados = {
            codigo: nombre
            for codigo, nombre in medios.items()
            if nombre.lower() != "lanacion"
        }

        # Mapeos especiales para nombres bonitos
        nombres_especiales = {
            "google_news": "Google News"
        }

        competencias = {}

        
        for codigo, nombre in medios_filtrados.items():
            nombre_bonito = nombres_especiales.get(nombre.lower(), nombre.capitalize())
            competencias[nombre] = (codigo, nombre_bonito)

        
        competencias["google_trends"] = ("00", "Google Trends")

        return JSONResponse(
            content=competencias,
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": f"Error al obtener competencias: {str(e)}"},
            status_code=500
        )
