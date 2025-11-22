from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Article(BaseModel):
    title: str
    link: str
    time: str
    source: str
    query: str


class TrendsRequest(BaseModel):
    keywords: List[str] = Field(default_factory= lambda:["Argentina"])
    timeframe: str = "today 3-m"
    geo: str = ""


class TrendsResponse(BaseModel):
    interest_over_time: Dict[str, Any]
    related_queries: Dict[str, Any]
    interest_by_region: Dict[str, Any]


class DailyTrendsRequest(BaseModel):
    country: str = "Ar"


class NewsRequest(BaseModel):
    query: str = "tecnología"
    num_articles: int = 10


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


class DiariosRequest(BaseModel):
    codigo: str


class LaNacionNewsCategory(BaseModel):
    categoria: str
