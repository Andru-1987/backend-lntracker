from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from utils.db_check_cnx import ensure_db_connection
from services.db_service_data import NewsWareHouseData
from utils.config import settings
from models.models import LaNacionNewsCategory

router = APIRouter()


@router.post("/lanacion_by_category")
async def obtener_noticias_por_categoria(categoria:LaNacionNewsCategory, request:Request ):
    await ensure_db_connection(request)

    try:
        retriever = NewsWareHouseData(request.app.state.mssql)

        from_msserver = retriever.get_all_news_category_list(categoria.categoria)
        
        data ={}

        data["data"] = from_msserver
        data["total"] = len(from_msserver)


        return JSONResponse(
            content=data,
            status_code=200,
            media_type="application/json"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener noticias: {str(e)}")
