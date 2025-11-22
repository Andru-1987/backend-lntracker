import httpx
from fastapi_cache import FastAPICache
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Response # Agregamos Response aquí
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware # Importamos la base del Middleware
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette.requests import Request
from typing import Callable, Awaitable

from utils.server_services import MSServerConnector
from utils.config import settings
from utils.server_services import MSServerConnector
from api.route import trends_routes, system_routes,filter_lanacion_routes, scrapper_routes, lanacion_news, llm_process_routes

import vertexai

# GLOBAL MIDDLEWARE PARA ENCABEZADOS
class GlobalHeaderMiddleware(BaseHTTPMiddleware):
    """
    Añade el encabezado 'Accept-Encoding: gzip' a todas las respuestas HTTP.
    """
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        
        # 1. Procesa la solicitud y obtiene la respuesta de la ruta (handler)
        response = await call_next(request)
        
        # 2. Agrega el encabezado deseado
        response.headers["Accept-Encoding"] = "gzip"
        
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):

    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    print(" Caché en Memoria (RAM) activado")
    
    # 1. Inicialización de Vertex AI (Suele ser segura ya que es config local)
    try:
        vertexai.init(
            project=settings.VERTEX_PROJECT_ID,
            location=settings.VERTEX_LOCATION
        )
        app.state.vertex = {
            "project": settings.VERTEX_PROJECT_ID,
            "location": settings.VERTEX_LOCATION
        }
        print("Vertex AI inicializado")
    except Exception as e:
        print(f"Error inicializando Vertex AI: {e}")

    # 2. Inicialización del conector SQL
    app.state.mssql = MSServerConnector(
        server=settings.DATABASE_SERVER,
        database=settings.DATABASE,
        username=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD
    )
    
    # Estado inicial
    app.state.db_status = "disconnected"
    app.state.fallback_available = False

    # 3. Intento de Conexión a SQL Server
    try:
        print("Intentando conectar a MS SQL...")
        app.state.mssql.connect()
        print("MS SQL conectado con éxito")
        app.state.db_status = "connected"
        
    except Exception as e:
        print(f"Falló la conexión a MS SQL (Driver/Red): {e}")
        app.state.db_status = "error"

        forward_client_url = settings.EXTERNAL_API_URL # Asegúrate de tener esta variable en settings
        
        print(f"Verificando disponibilidad de Fallback API: {forward_client_url}")
        
        try:
            # Timeout corto para no bloquear el arranque demasiado tiempo
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{forward_client_url}/health")
                
                if response.status_code == 200:
                    print("Fallback API está DISPONIBLE. Se usará como respaldo.")
                    app.state.fallback_available = True
                else:
                    print(f"Fallback API respondió con estado: {response.status_code}")
        except Exception as http_ex:
            print(f"No se pudo contactar al Fallback API: {http_ex}")

    yield 

    print("🛑 Apagando aplicación...")
    
    if app.state.db_status == "connected":
        try:
            app.state.mssql.disconnect()
            print("MS SQL desconectado correctamente")
        except Exception as e:
            print(f"Error al desconectar MS SQL: {e}")


# Configuración de FastAPI
app = FastAPI(
    lifespan=lifespan,
    title="Google News & Trends API",
    description="API modular para obtener noticias y trends",
    version="2.0.0",
)

# 1. Aplicar el Middleware para añadir el encabezado "Accept-Encoding: gzip"
app.add_middleware(GlobalHeaderMiddleware)

# 2. Aplicar el GZipMiddleware nativo (para COMPRIMIR respuestas grandes)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 3. Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
# rutas de auth
# app.include_router(auth.router,tags=["AuthenticationPassWordless"])

app.include_router(system_routes.router, tags=["System"])

app.include_router(filter_lanacion_routes.router, prefix="/api", tags=["ColdStart"])
app.include_router(trends_routes.router, prefix="/api", tags=["Trends"])
app.include_router(lanacion_news.router, prefix="/api", tags=["LaNacion"])
app.include_router(scrapper_routes.router, prefix="/api", tags=["Benchmarks News"])
app.include_router(llm_process_routes.router, prefix="/llm", tags=["BenchMark Coincidencias"])


@app.get("/",tags=["LN Track"])
async def root():
    return {
        "message": "Google News & Trends Rss (Modular)",
        "version": "1.0.0",
    }