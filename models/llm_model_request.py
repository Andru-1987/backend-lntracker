from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PromptRequest(BaseModel):
    competencia:str
    competencia_code:str
    categoria:str
