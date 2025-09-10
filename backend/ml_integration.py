"""
Integração do modelo ML com o backend.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging

# Adicionar o diretório ml ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))

logger = logging.getLogger(__name__)

class MLModelIntegration:
    """Classe para integrar o modelo ML treinado com o backend."""
    
    def __init__(self, model_path: str = None):
        """
        Inicializa a integração com o modelo ML.
        
        Args:
            model_path: Caminho para o modelo treinado
        """
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), '..', 'ml', 'core', 'models', 'malaria_risk_model_expanded.pkl'
        )
        self.municipio_encoder_path = os.path.join(
            os.path.dirname(__file__), '..', 'ml', 'core', 'models', 'label_encoder_municipio_expanded.pkl'
        )
        self.risco_encoder_path = os.path.join(
            os.path.dirname(__file__), '..', 'ml', 'core', 'models', 'label_encoder_risco_expanded.pkl'
        )
        
        self.model = None
        self.municipio_encoder = None
        self.risco_encoder = None
        self.feature_columns = None
        
        self._load_model()
    
    def _load_model(self) -> bool:
        """Carrega o modelo e encoders treinados."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Modelo carregado de: {self.model_path}")
            else:
                logger.warning(f"Modelo não encontrado em: {self.model_path}")
                return False
            
            if os.path.exists(self.municipio_encoder_path):
                self.municipio_encoder = joblib.load(self.municipio_encoder_path)
                logger.info(f"Encoder de município carregado")
            
            if os.path.exists(self.risco_encoder_path):
                self.risco_encoder = joblib.load(self.risco_encoder_path)
                logger.info(f"Encoder de risco carregado")
            
            # Definir colunas de features esperadas (27 features do modelo treinado)
            self.feature_columns = [
                'Ano', 'Semana', 'Temperatura_Media_C', 'Precipitacao_mm', 'semana_sin',
                'semana_cos', 'tendencia', 'estacao', 'temp_norm', 'precip_norm', 'casos_lag1',
                'casos_lag2', 'casos_lag3', 'casos_ma3', 'casos_ma5', 'casos_ma10',
                'municipio_encoded', 'temp_precip_interaction', 'casos_temp_interaction',
                'casos_precip_interaction', 'municipio_casos_mean', 'municipio_casos_std',
                'municipio_casos_min', 'municipio_casos_max', 'casos_vs_municipio_mean',
                'temp_vs_historical', 'precip_vs_historical'
            ]
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def is_model_loaded(self) -> bool:
        """Verifica se o modelo está carregado."""
        return self.model is not None
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para predição baseado no modelo treinado.
        
        Args:
            data: DataFrame com dados históricos
            
        Returns:
            DataFrame com features preparadas
        """
        try:
            df = data.copy()
            
            # Mapear colunas para nomes esperados
            column_mapping = {
                'casos': 'Casos_Malaria',
                'temp_media_c': 'Temperatura_Media_C',
                'chuva_mm': 'Precipitacao_mm',
                'data': 'data'
            }
            
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and new_name not in df.columns:
                    df[new_name] = df[old_name]
            
            # Garantir que temos as colunas necessárias
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'])
                df['Ano'] = df['data'].dt.year
                df['Semana'] = df['data'].dt.isocalendar().week.astype(int)
            else:
                # Se não temos data, usar valores padrão
                df['Ano'] = 2024
                df['Semana'] = 1
            
            # Adicionar colunas padrão se não existirem
            if 'Municipio' not in df.columns:
                df['Municipio'] = 'Kuito'
            
            # Features temporais cíclicas
            df['semana_sin'] = np.sin(2 * np.pi * df['Semana'] / 52)
            df['semana_cos'] = np.cos(2 * np.pi * df['Semana'] / 52)
            
            # Tendência temporal
            df['tendencia'] = df.index
            
            # Estação do ano (simplificada para Angola)
            df['estacao'] = ((df['Semana'] - 1) // 13) + 1
            
            # Normalização de temperatura e precipitação
            df['temp_norm'] = (df['Temperatura_Media_C'] - df['Temperatura_Media_C'].mean()) / df['Temperatura_Media_C'].std()
            df['precip_norm'] = (df['Precipitacao_mm'] - df['Precipitacao_mm'].mean()) / df['Precipitacao_mm'].std()
            
            # Features de lag para casos
            df['casos_lag1'] = df['Casos_Malaria'].shift(1)
            df['casos_lag2'] = df['Casos_Malaria'].shift(2)
            df['casos_lag3'] = df['Casos_Malaria'].shift(3)
            
            # Médias móveis
            df['casos_ma3'] = df['Casos_Malaria'].rolling(window=3, min_periods=1).mean()
            df['casos_ma5'] = df['Casos_Malaria'].rolling(window=5, min_periods=1).mean()
            df['casos_ma10'] = df['Casos_Malaria'].rolling(window=10, min_periods=1).mean()
            
            # Encoding de município (simplificado)
            df['municipio_encoded'] = 0  # Kuito = 0
            
            # Features de interação
            df['temp_precip_interaction'] = df['Temperatura_Media_C'] * df['Precipitacao_mm']
            df['casos_temp_interaction'] = df['Casos_Malaria'] * df['Temperatura_Media_C']
            df['casos_precip_interaction'] = df['Casos_Malaria'] * df['Precipitacao_mm']
            
            # Estatísticas por município (simplificadas)
            df['municipio_casos_mean'] = df['Casos_Malaria'].mean()
            df['municipio_casos_std'] = df['Casos_Malaria'].std()
            df['municipio_casos_min'] = df['Casos_Malaria'].min()
            df['municipio_casos_max'] = df['Casos_Malaria'].max()
            
            # Comparações com histórico
            df['casos_vs_municipio_mean'] = df['Casos_Malaria'] / df['municipio_casos_mean']
            df['temp_vs_historical'] = df['Temperatura_Media_C'] / df['Temperatura_Media_C'].mean()
            df['precip_vs_historical'] = df['Precipitacao_mm'] / df['Precipitacao_mm'].mean()
            
            # Preencher valores NaN
            df = df.fillna(0)
            
            # Selecionar apenas as colunas de features na ordem correta
            feature_df = df[self.feature_columns].copy()
            
            return feature_df
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            raise
    
    def predict_risk(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Faz predição de risco de malária.
        
        Args:
            data: DataFrame com dados históricos
            
        Returns:
            Dicionário com resultados da predição
        """
        try:
            if not self.is_model_loaded():
                raise ValueError("Modelo não está carregado")
            
            # Preparar features
            features = self.prepare_features(data)
            
            # Fazer predição
            prediction = self.model.predict(features.iloc[-1:].values)
            probabilities = self.model.predict_proba(features.iloc[-1:].values)
            
            # Decodificar predição se encoder disponível
            if self.risco_encoder is not None:
                risk_class = self.risco_encoder.inverse_transform(prediction)[0]
            else:
                risk_class = prediction[0]
            
            # Calcular probabilidades por classe
            if len(probabilities[0]) == 3:
                prob_baixo = float(probabilities[0][0])
                prob_medio = float(probabilities[0][1])
                prob_alto = float(probabilities[0][2])
            else:
                # Se apenas 2 classes, distribuir probabilidades
                prob_baixo = float(1 - probabilities[0][0])
                prob_medio = 0.0
                prob_alto = float(probabilities[0][0])
            
            # Calcular score de risco (média ponderada)
            risk_score = (prob_baixo * 1 + prob_medio * 2 + prob_alto * 3) / 3
            
            return {
                'classe_risco': risk_class,
                'score_risco': float(risk_score),
                'probabilidade_baixo': prob_baixo,
                'probabilidade_medio': prob_medio,
                'probabilidade_alto': prob_alto,
                'features_used': self.feature_columns,
                'model_version': 'expanded_v1.0'
            }
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo carregado."""
        return {
            'model_loaded': self.is_model_loaded(),
            'model_path': self.model_path,
            'feature_columns': self.feature_columns,
            'model_type': type(self.model).__name__ if self.model else None,
            'municipio_encoder_loaded': self.municipio_encoder is not None,
            'risco_encoder_loaded': self.risco_encoder is not None
        }

# Instância global para uso na API
ml_integration = MLModelIntegration()


