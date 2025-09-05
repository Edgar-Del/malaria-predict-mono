"""
Endpoints da API FastAPI para o Sistema de Previsão de Risco de Malária (Bié).
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from src.model.malaria_model import MalariaModel
from src.features.feature_engineering import FeatureEngineer
from src.ingest.database_manager import DatabaseManager
from src.api.models import PredictionRequest, PredictionResponse, TrainingResponse, MetricsResponse

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter()

# Inicializar componentes
feature_engineer = FeatureEngineer()

# Dependências
def get_malaria_model():
    malaria_model = MalariaModel()
    model_path = os.getenv('MODEL_PATH', 'models/malaria_model.joblib')
    if not malaria_model.load_model(model_path):
        logger.warning("Modelo não encontrado, será necessário treinar")
    return malaria_model

@router.get("/")
async def root():
    """Endpoint raiz com informações básicas."""
    return {
        "message": "Sistema de Previsão de Risco de Malária (Bié)",
        "version": "1.0.0",
        "status": "ativo",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check(db: DatabaseManager = Depends()):
    """Verificação de saúde da API."""
    try:
        # Verificar conexão com banco
        db_ok = db.test_connection()
        
        # Verificar modelo
        model = get_malaria_model()
        model_ok = model.model is not None
        
        return {
            "status": "healthy" if db_ok and model_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "model": "loaded" if model_ok else "not_loaded",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@router.post("/train", response_model=TrainingResponse)
async def train_model(background_tasks: BackgroundTasks, db: DatabaseManager = Depends()):
    """
    Treina o modelo com dados atuais.
    """
    try:
        start_time = datetime.now()
        logger.info("Iniciando treinamento do modelo")
        
        # Carregar dados
        series_df = db.get_series_semanais()
        if series_df.empty:
            raise HTTPException(status_code=400, detail="Nenhum dado encontrado para treinamento")
        
        # Criar features
        df_with_features = feature_engineer.create_all_features(series_df)
        
        # Treinar modelo
        malaria_model = MalariaModel(model_type='random_forest')
        X, y = malaria_model.prepare_data(df_with_features)
        metrics = malaria_model.train(X, y)
        
        # Salvar modelo
        model_path = os.getenv('MODEL_PATH', 'models/malaria_model.joblib')
        malaria_model.save_model(model_path)
        
        # Salvar métricas no banco
        metrics_db = {
            'modelo_versao': metrics['model_version'],
            'modelo_tipo': 'RandomForest',
            'data_treinamento': datetime.now(),
            'accuracy': metrics['accuracy'],
            'precision_macro': metrics['precision_macro'],
            'recall_macro': metrics['recall_macro'],
            'f1_macro': metrics['f1_macro'],
            'precision_baixo': metrics.get('precision_baixo'),
            'recall_baixo': metrics.get('recall_baixo'),
            'f1_baixo': metrics.get('f1_baixo'),
            'precision_medio': metrics.get('precision_medio'),
            'recall_medio': metrics.get('recall_medio'),
            'f1_medio': metrics.get('f1_medio'),
            'precision_alto': metrics.get('precision_alto'),
            'recall_alto': metrics.get('recall_alto'),
            'f1_alto': metrics.get('f1_alto'),
            'parametros': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            }
        }
        
        db.insert_metricas(metrics_db)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Treinamento concluído em {training_time:.2f}s")
        
        return TrainingResponse(
            status="success",
            modelo_versao=metrics['model_version'],
            metrics=metrics,
            training_time=training_time,
            message="Modelo treinado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {str(e)}")

@router.get("/predict", response_model=PredictionResponse)
async def predict_risk(
    municipio: str = Query(..., description="Nome do município"),
    ano_semana: str = Query(..., description="Ano-semana no formato YYYY-WW"),
    db: DatabaseManager = Depends()
):
    """
    Obtém previsão de risco para um município e semana específicos.
    """
    try:
        # Verificar se modelo está carregado
        model = get_malaria_model()
        if model.model is None:
            raise HTTPException(status_code=400, detail="Modelo não treinado. Execute /train primeiro.")
        
        # Obter dados históricos do município
        series_df = db.get_series_semanais()
        municipio_data = series_df[series_df['municipio_nome'] == municipio]
        
        if municipio_data.empty:
            raise HTTPException(status_code=404, detail=f"Município '{municipio}' não encontrado")
        
        # Criar features
        df_with_features = feature_engineer.create_all_features(municipio_data)
        
        # Preparar dados para predição
        X, _ = model.prepare_data(df_with_features)
        
        # Fazer predição
        y_pred, y_pred_proba = model.predict(X)
        
        # Obter última predição (mais recente)
        last_prediction = y_pred[-1]
        last_probabilities = y_pred_proba[-1]
        
        # Calcular score de risco
        risk_score = model.predict_risk_score(X).iloc[-1]
        
        # Decodificar classe de risco
        if hasattr(model.label_encoder, 'classes_'):
            class_names = model.label_encoder.classes_
            if len(class_names) == 3:
                prob_baixo = last_probabilities[0]
                prob_medio = last_probabilities[1]
                prob_alto = last_probabilities[2]
            else:
                prob_baixo = 1 - last_probabilities[0] if len(last_probabilities) == 1 else last_probabilities[0]
                prob_medio = 0
                prob_alto = last_probabilities[0] if len(last_probabilities) == 1 else last_probabilities[1]
        else:
            prob_baixo = prob_medio = prob_alto = 0.33
        
        # Salvar previsão no banco
        previsao_data = {
            'municipio_id': municipio_data['municipio_id'].iloc[-1],
            'ano_semana_prevista': ano_semana,
            'classe_risco': last_prediction,
            'score_risco': float(risk_score),
            'probabilidade_baixo': float(prob_baixo),
            'probabilidade_medio': float(prob_medio),
            'probabilidade_alto': float(prob_alto),
            'modelo_versao': model.model_version or 'v1.0.0',
            'modelo_tipo': 'RandomForest'
        }
        
        db.insert_previsoes(pd.DataFrame([previsao_data]))
        
        return PredictionResponse(
            municipio=municipio,
            ano_semana=ano_semana,
            classe_risco=last_prediction,
            score_risco=float(risk_score),
            probabilidade_baixo=float(prob_baixo),
            probabilidade_medio=float(prob_medio),
            probabilidade_alto=float(prob_alto),
            modelo_versao=model.model_version or 'v1.0.0',
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@router.get("/previsoes/semana/{ano_semana}")
async def get_weekly_predictions(
    ano_semana: str,
    db: DatabaseManager = Depends()
):
    """
    Obtém todas as previsões para uma semana específica.
    """
    try:
        previsoes_df = db.get_previsoes(ano_semana=ano_semana)
        
        if previsoes_df.empty:
            return {"previsoes": [], "total": 0}
        
        previsoes = []
        for _, row in previsoes_df.iterrows():
            previsoes.append({
                "municipio": row['municipio_nome'],
                "municipio_id": row['municipio_id'],
                "ano_semana": row['ano_semana_prevista'],
                "classe_risco": row['classe_risco'],
                "score_risco": float(row['score_risco']),
                "probabilidade_baixo": float(row['probabilidade_baixo'] or 0),
                "probabilidade_medio": float(row['probabilidade_medio'] or 0),
                "probabilidade_alto": float(row['probabilidade_alto'] or 0),
                "modelo_versao": row['modelo_versao'],
                "created_at": row['created_at'].isoformat()
            })
        
        return {
            "previsoes": previsoes,
            "total": len(previsoes),
            "ano_semana": ano_semana
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter previsões: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter previsões: {str(e)}")

@router.get("/metrics/latest", response_model=MetricsResponse)
async def get_latest_metrics(db: DatabaseManager = Depends()):
    """
    Obtém as últimas métricas do modelo.
    """
    try:
        metrics = db.get_metricas_latest()
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Nenhuma métrica encontrada")
        
        return MetricsResponse(
            modelo_versao=metrics['modelo_versao'],
            accuracy=float(metrics['accuracy']),
            precision_macro=float(metrics['precision_macro']),
            recall_macro=float(metrics['recall_macro']),
            f1_macro=float(metrics['f1_macro']),
            precision_baixo=float(metrics['precision_baixo']) if metrics['precision_baixo'] else None,
            recall_baixo=float(metrics['recall_baixo']) if metrics['recall_baixo'] else None,
            f1_baixo=float(metrics['f1_baixo']) if metrics['f1_baixo'] else None,
            precision_medio=float(metrics['precision_medio']) if metrics['precision_medio'] else None,
            recall_medio=float(metrics['recall_medio']) if metrics['recall_medio'] else None,
            f1_medio=float(metrics['f1_medio']) if metrics['f1_medio'] else None,
            precision_alto=float(metrics['precision_alto']) if metrics['precision_alto'] else None,
            recall_alto=float(metrics['recall_alto']) if metrics['recall_alto'] else None,
            f1_alto=float(metrics['f1_alto']) if metrics['f1_alto'] else None,
            data_treinamento=metrics['data_treinamento']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")

@router.get("/municipios")
async def get_municipios(db: DatabaseManager = Depends()):
    """
    Obtém lista de municípios.
    """
    try:
        municipios = db.get_municipios()
        return {"municipios": municipios, "total": len(municipios)}
    except Exception as e:
        logger.error(f"Erro ao obter municípios: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter municípios: {str(e)}")

@router.get("/series/{municipio}")
async def get_municipality_series(
    municipio: str,
    limit: int = Query(52, description="Número máximo de registros"),
    db: DatabaseManager = Depends()
):
    """
    Obtém série temporal de um município específico.
    """
    try:
        # Obter ID do município
        municipios = db.get_municipios()
        municipio_id = None
        for m in municipios:
            if m['nome'].lower() == municipio.lower():
                municipio_id = m['id']
                break
        
        if not municipio_id:
            raise HTTPException(status_code=404, detail=f"Município '{municipio}' não encontrado")
        
        # Obter série temporal
        series_df = db.get_series_semanais(municipio_id=municipio_id, limit=limit)
        
        if series_df.empty:
            return {"series": [], "municipio": municipio, "total": 0}
        
        series = []
        for _, row in series_df.iterrows():
            series.append({
                "ano_semana": row['ano_semana'],
                "casos": int(row['casos']),
                "chuva_mm": float(row['chuva_mm']) if pd.notna(row['chuva_mm']) else None,
                "temp_media_c": float(row['temp_media_c']) if pd.notna(row['temp_media_c']) else None,
                "created_at": row['created_at'].isoformat()
            })
        
        return {
            "series": series,
            "municipio": municipio,
            "total": len(series)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter série temporal: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter série temporal: {str(e)}")
