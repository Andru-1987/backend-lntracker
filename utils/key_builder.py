from fastapi import Response
from fastapi import Request
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
import hashlib
import json

from models.llm_model_request import PromptRequest

# Función para generar clave de caché basada en el body
def request_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    """Genera clave de caché incluyendo el body de la request"""
    # Obtener el PromptRequest del kwargs
    prompt_request: PromptRequest = kwargs.get("prompt_request")
    
    # Crear un hash del contenido relevante
    cache_key_data = {
        "competencia": prompt_request.competencia,
        "competencia_code": prompt_request.competencia_code,
        "categoria": prompt_request.categoria
    }
    
    # Generar hash
    key_hash = hashlib.md5(
        json.dumps(cache_key_data, sort_keys=True).encode()
    ).hexdigest()
    
    return f"{namespace}:{func.__name__}:{key_hash}"
