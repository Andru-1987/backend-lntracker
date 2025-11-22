# config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import time
from typing import List


class Settings(BaseSettings):

    # Configuración de FastAPI
    APP_NAME: str = Field(default="FastAPI Application", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")

    
    # Configuración del servidor
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8080, env="PORT")
    
    # Base de datos
    DATABASE_USER: str = Field(env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field(env="DATABASE_PASSWORD")
    DATABASE: str = Field(env="DATABASE")
    DATABASE_SERVER: str = Field(env="DATABASE_SERVER")
    
    
    # Seguridad
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # External APIs
    EXTERNAL_API_URL: str = Field(default="https://api.example.com", env="EXTERNAL_API_URL")
  
    VERTEX_PROJECT_ID:str= Field( default="motor-club-ln", env="VERTEX_PROJECT_ID")
    VERTEX_LOCATION:str= Field( default= "us-central1", env="VERTEX_LOCATION")
    VERTEX_MODEL:str= Field(default="gemini-2.5-flash-lite" , env="VERTEX_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
settings = Settings()