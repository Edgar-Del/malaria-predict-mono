"""
Modelo de predição para integração com o backend.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import joblib
import json

# Adicionar o diretório ml do projeto principal ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../ml'))

logger = logging.getLogger(__name__)

class ModelPredictor:
    """Classe para predição de risco de malária."""
    
    def __init__(self):
        self.model = None
        self.feature_columns = []
        self.model_version = None
        self.is_loaded = False
        
    async def load_model(self, model_path: Optional[str] = None):
        """Carrega o modelo treinado."""
        try:
            if model_path is None:
                model_path = "../ml/core/models/malaria_risk_model_backend.pkl"
            
            if not os.path.exists(model_path):
                # Tentar carregar modelo do ML principal
                alt_path = "../../ml/core/models/malaria_risk_model_expanded.pkl"
                if os.path.exists(alt_path):
                    model_path = alt_path
                else:
                    raise FileNotFoundError("Modelo não encontrado")
            
            self.model = joblib.load(model_path)
            
            # Carregar metadados
            metadata_path = model_path.replace('.pkl', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_columns = metadata.get('feature_columns', [])
                    self.model_version = metadata.get('model_version', 'unknown')
            else:
                # Valores padrão
                self.feature_columns = [
                    'chuva_mm', 'temp_media_c', 'temp_min_c', 'temp_max_c',
                    'umidade_relativa', 'casos_lag1', 'casos_lag2', 'casos_lag3',
                    'casos_lag4', 'casos_media_2s', 'casos_media_4s'
                ]
                self.model_version = 'unknown'
            
            self.is_loaded = True
            logger.info(f"Modelo carregado: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    async def predict_single(
        self,
        municipio: str,
        ano_semana: str,
        db_manager
    ) -> Optional[Dict[str, Any]]:
        """
        Faz predição para um município específico.
        
        Args:
            municipio: Nome do município
            ano_semana: Ano-semana no formato YYYY-WW
            db_manager: Gerenciador de banco de dados
            
        Returns:
            Dict com resultado da predição
        """
        try:
            if not self.is_loaded:
                await self.load_model()
            
            # Obter dados históricos do município
            dados_historicos = await self._get_historical_data(municipio, db_manager)
            
            if dados_historicos.empty:
                logger.warning(f"Nenhum dado histórico encontrado para {municipio}")
                return None
            
            # Preparar features para predição
            features = self._prepare_prediction_features(dados_historicos, ano_semana)
            
            if features is None:
                logger.warning(f"Features insuficientes para predição em {municipio}")
                return None
            
            # Fazer predição
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            
            # Mapear classes
            class_mapping = {0: 'baixo', 1: 'medio', 2: 'alto'}
            classe_risco = class_mapping.get(prediction, 'baixo')
            
            # Calcular score de risco (probabilidade da classe predita)
            score_risco = probabilities[prediction]
            
            # Preparar probabilidades por classe
            prob_baixo = probabilities[0] if len(probabilities) > 0 else 0.0
            prob_medio = probabilities[1] if len(probabilities) > 1 else 0.0
            prob_alto = probabilities[2] if len(probabilities) > 2 else 0.0
            
            return {
                'municipio': municipio,
                'ano_semana_prevista': ano_semana,
                'classe_risco': classe_risco,
                'score_risco': float(score_risco),
                'probabilidade_baixo': float(prob_baixo),
                'probabilidade_medio': float(prob_medio),
                'probabilidade_alto': float(prob_alto),
                'modelo_versao': self.model_version,
                'modelo_tipo': 'RandomForest',
                'created_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro na predição para {municipio}: {e}")
            return None
    
    async def _get_historical_data(self, municipio: str, db_manager) -> pd.DataFrame:
        """Obtém dados históricos do município."""
        try:
            # Por enquanto, carregar dados do CSV
            # Em produção, isso viria do banco de dados
            data_path = "../../data/raw/malaria_bie_expanded.csv"
            
            if not os.path.exists(data_path):
                data_path = "../../data/raw/malaria_bie.csv"
            
            df = pd.read_csv(data_path)
            
            # Filtrar por município
            df_municipio = df[df['municipio'].str.lower() == municipio.lower()]
            
            return df_municipio
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {e}")
            return pd.DataFrame()
    
    def _prepare_prediction_features(self, df: pd.DataFrame, ano_semana: str) -> Optional[list]:
        """Prepara features para predição."""
        try:
            if df.empty:
                return None
            
            # Pegar o último registro disponível
            last_record = df.iloc[-1]
            
            # Preparar features
            features = []
            for col in self.feature_columns:
                if col in last_record:
                    features.append(float(last_record[col]) if pd.notna(last_record[col]) else 0.0)
                else:
                    features.append(0.0)
            
            # Adicionar features temporais se necessário
            if 'ano' in self.feature_columns and 'ano_semana' in last_record:
                ano, semana = ano_semana.split('-')
                features.append(int(ano))
                features.append(int(semana))
            
            return features
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return None
    
    async def predict_batch(
        self,
        municipios: list,
        ano_semana: str,
        db_manager
    ) -> list:
        """
        Faz predições para múltiplos municípios.
        
        Args:
            municipios: Lista de municípios
            ano_semana: Ano-semana no formato YYYY-WW
            db_manager: Gerenciador de banco de dados
            
        Returns:
            Lista com resultados das predições
        """
        try:
            predictions = []
            
            for municipio in municipios:
                prediction = await self.predict_single(municipio, ano_semana, db_manager)
                if prediction:
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro na predição em lote: {e}")
            return []
