"""
Modelos Pydantic para a API FastAPI.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# Modelos de Previsão
class PrevisaoRequest(BaseModel):
    municipio: str = Field(..., description="Nome do município")
    ano_semana: str = Field(..., description="Ano-semana no formato YYYY-WW")

class PrevisaoResponse(BaseModel):
    municipio: str
    ano_semana_prevista: str
    classe_risco: str
    score_risco: float
    probabilidade_baixo: float
    probabilidade_medio: float
    probabilidade_alto: float
    modelo_versao: str
    modelo_tipo: str
    created_at: datetime

class PrevisoesSemanaResponse(BaseModel):
    ano_semana: str
    previsoes: List[PrevisaoResponse]
    total_municipios: int
    municipios_alto_risco: int
    municipios_medio_risco: int
    municipios_baixo_risco: int

# Modelos de Treinamento
class TreinamentoRequest(BaseModel):
    municipios: Optional[List[str]] = Field(None, description="Lista de municípios para treinar")
    test_size: float = Field(0.2, ge=0.1, le=0.5, description="Proporção de dados para teste")
    random_state: int = Field(42, description="Seed para reprodutibilidade")
    retreinar: bool = Field(False, description="Forçar retreinamento mesmo se modelo existir")

class TreinamentoResponse(BaseModel):
    status: str
    modelo_versao: str
    metricas: Dict[str, Any]
    tempo_treinamento_segundos: float
    registros_treinamento: int
    registros_teste: int

class MetricasModeloResponse(BaseModel):
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

# Modelos de Dados
class MunicipioResponse(BaseModel):
    id: int
    nome: str
    cod_ibge_local: Optional[str]
    latitude: float
    longitude: float
    populacao: Optional[int]
    area_km2: Optional[float]

class SerieSemanalResponse(BaseModel):
    municipio: str
    ano_semana: str
    casos: int
    chuva_mm: Optional[float]
    temp_media_c: Optional[float]
    temp_min_c: Optional[float]
    temp_max_c: Optional[float]
    umidade_relativa: Optional[float]
    casos_lag1: Optional[int]
    casos_lag2: Optional[int]
    casos_lag3: Optional[int]
    casos_lag4: Optional[int]
    casos_media_2s: Optional[float]
    casos_media_4s: Optional[float]

class DadosHistoricoRequest(BaseModel):
    municipio: str
    ano_semana: str
    casos: int
    chuva_mm: Optional[float]
    temp_media_c: Optional[float]
    temp_min_c: Optional[float]
    temp_max_c: Optional[float]
    umidade_relativa: Optional[float]

# Modelos de Alertas
class AlertaResponse(BaseModel):
    id: int
    municipio: str
    ano_semana: str
    classe_risco: str
    score_risco: float
    email_enviado: bool
    data_envio: Optional[datetime]
    destinatarios: List[str]

class ConfiguracaoAlertaRequest(BaseModel):
    threshold_alto_risco: float = Field(0.7, ge=0.0, le=1.0)
    threshold_medio_risco: float = Field(0.4, ge=0.0, le=1.0)
    email_destinatarios: List[str]
    enviar_alertas_automaticos: bool = True

class ConfiguracaoAlertaResponse(BaseModel):
    threshold_alto_risco: float
    threshold_medio_risco: float
    email_destinatarios: List[str]
    enviar_alertas_automaticos: bool
    ultima_atualizacao: datetime

# Modelos de Estatísticas e Relatórios
class EstatisticasMunicipioResponse(BaseModel):
    municipio: str
    total_casos_ano: int
    media_casos_semana: float
    max_casos_semana: int
    min_casos_semana: int
    semanas_alto_risco: int
    semanas_medio_risco: int
    semanas_baixo_risco: int
    tendencia_ultimas_4_semanas: str

class RelatorioSemanalResponse(BaseModel):
    ano_semana: str
    total_casos_previstos: int
    municipios_alto_risco: List[str]
    municipios_medio_risco: List[str]
    municipios_baixo_risco: List[str]
    recomendacoes: List[str]
    alertas_enviados: int

# Modelos de Resposta Genérica
class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime

# Modelos de Compatibilidade (manter para compatibilidade)
PredictionRequest = PrevisaoRequest
PredictionResponse = PrevisaoResponse
TrainingResponse = TreinamentoResponse
MetricsResponse = MetricasModeloResponse