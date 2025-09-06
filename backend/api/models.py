"""
Modelos Pydantic para a API FastAPI.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    municipio: str = Field(..., description="Nome do município")
    ano_semana: str = Field(..., description="Ano-semana no formato YYYY-WW")

class PredictionResponse(BaseModel):
    municipio: str
    ano_semana: str
    classe_risco: str
    score_risco: float
    probabilidade_baixo: float
    probabilidade_medio: float
    probabilidade_alto: float
    modelo_versao: str
    created_at: datetime
class TrainingResponse(BaseModel):
    status: str
    modelo_versao: str
    metrics: Dict[str, Any]
    training_time: float
    message: str
class MetricsResponse(BaseModel):
    modelo_versao: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_baixo: Optional[float]
    recall_baixo: Optional[float]
    f1_baixo: Optional[float]
    precision_medio: Optional[float]
    recall_medio: Optional[float]
    f1_medio: Optional[float]
    precision_alto: Optional[float]
    recall_alto: Optional[float]
    f1_alto: Optional[float]
    data_treinamento: datetime