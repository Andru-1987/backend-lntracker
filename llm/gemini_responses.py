import json
from llm.query_prompt_v01 import prompt
from vertexai.generative_models import GenerativeModel
from utils.config import settings

JSON_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "resumen_ejecutivo": {
            "type": "OBJECT",
            "properties": {
                "total_competencia": {
                    "type": "INTEGER", 
                    "description": "Número total de noticias de la competencia que caen en la categoría."
                },
                "coincidencias_detectadas": {
                    "type": "INTEGER", 
                    "description": "Número de noticias de la competencia que coinciden con Mis noticias."
                },
                "brechas_cobertura": {
                    "type": "INTEGER", 
                    "description": "Número de temas únicos de la competencia (brechas)."
                }
            },
            "required": ["total_competencia", "coincidencias_detectadas", "brechas_cobertura"]
        },
        
        "clasificadas_en_categoria": {
            "type": "ARRAY",
            "description": "Lista de noticias de la competencia filtradas por la categoría objetivo.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "noticia": {
                        "type": "STRING", 
                        "description": "Título original de la noticia de la competencia."
                    },
                    "etiquetas": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"}, 
                        "description": "Etiquetas temáticas asignadas a esta noticia."
                    },
                    "relevancia": {
                        "type": "STRING", 
                        "description": "Relevancia: alta, media o baja."
                    }
                },
                "required": ["noticia", "etiquetas", "relevancia"]
            }
        },
        
        "coincidencias": {
            "type": "ARRAY",
            "description": "Lista de pares de noticias que cubren el mismo evento/hecho.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "mi_noticia": {
                        "type": "STRING", 
                        "description": "Título de la noticia en la lista 'Mis noticias'."
                    },
                    "noticia_competencia": {
                        "type": "STRING", 
                        "description": "Título de la noticia de la competencia que coincide."
                    },
                    "motivo_coincidencia": {
                        "type": "STRING", 
                        "description": "Explicación breve de por qué se considera una coincidencia."
                    },
                    "etiquetas_comunes": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"}, 
                        "description": "Etiquetas temáticas que ambos titulares comparten."
                    }
                },
                "required": ["mi_noticia", "noticia_competencia", "motivo_coincidencia", "etiquetas_comunes"]
            }
        },
        
        "temas_competencia_unicos": {
            "type": "ARRAY",
            "description": "Lista de noticias de la competencia que NO tienen coincidencia (brechas de cobertura).",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "noticia": {
                        "type": "STRING", 
                        "description": "Título de la noticia única de la competencia."
                    },
                    "etiquetas": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"}, 
                        "description": "Etiquetas temáticas asignadas."
                    },
                    "por_que_es_brecha": {
                        "type": "STRING", 
                        "description": "Breve explicación de por qué esta noticia no fue cubierta."
                    },
                    "relevancia_para_mi_audiencia": {
                        "type": "STRING", 
                        "description": "Relevancia para la audiencia: alta, media o baja."
                    },
                    "oportunidad": {
                        "type": "STRING", 
                        "description": "Sugerencia de ángulo o enfoque para cubrir este tema."
                    }
                },
                "required": ["noticia", "etiquetas", "por_que_es_brecha", "relevancia_para_mi_audiencia", "oportunidad"]
            }
        },
        
        "analisis_tematico": {
            "type": "OBJECT",
            "properties": {
                "etiquetas_que_cubro": {
                    "type": "ARRAY", 
                    "items": {"type": "STRING"}, 
                    "description": "Temas (etiquetas) dominantes en 'Mis noticias'."
                },
                "etiquetas_que_no_cubro": {
                    "type": "ARRAY", 
                    "items": {"type": "STRING"}, 
                    "description": "Temas (etiquetas) dominantes encontrados solo en la competencia."
                },
                "recomendaciones": {
                    "type": "ARRAY", 
                    "items": {"type": "STRING"}, 
                    "description": "Recomendaciones estratégicas generales de cobertura."
                }
            },
            "required": ["etiquetas_que_cubro", "etiquetas_que_no_cubro", "recomendaciones"]
        }
    },
    "required": ["resumen_ejecutivo", "clasificadas_en_categoria", "coincidencias", "temas_competencia_unicos", "analisis_tematico"]
}

def analizar_noticias(lanacion_titulos, competencia_titulos, categoria):
    model = GenerativeModel(settings.VERTEX_MODEL)

    config = {
            "response_mime_type": "application/json",
            "response_schema": JSON_SCHEMA 
        }   

    prompt_formated= prompt.format(
            lanacion_titulos=lanacion_titulos,
            competencia_titulos=competencia_titulos,
            categoria=categoria
        )

    response = model.generate_content(prompt_formated, generation_config=config)
    try:
        return response.json
    except:
        return json.loads(response.text)
    