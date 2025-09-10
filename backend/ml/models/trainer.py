"""
Modelo de treinamento para integração com o backend.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Adicionar o diretório ml do projeto principal ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../ml'))

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Classe para treinamento de modelos de previsão de malária."""
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = []
        self.model_version = None
        
    async def train_model(
        self,
        db_manager,
        municipios: Optional[List[str]] = None,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Treina o modelo de previsão de malária.
        
        Args:
            db_manager: Gerenciador de banco de dados
            municipios: Lista de municípios para treinar (None = todos)
            test_size: Proporção de dados para teste
            random_state: Seed para reprodutibilidade
            
        Returns:
            Dict com resultados do treinamento
        """
        try:
            logger.info("Iniciando treinamento do modelo...")
            
            # Carregar dados do banco
            df = await self._load_training_data(db_manager, municipios)
            
            if df.empty:
                raise ValueError("Nenhum dado encontrado para treinamento")
            
            # Preparar dados
            X, y = self._prepare_features(df)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # Treinar modelo
            start_time = datetime.now()
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=random_state,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2
            )
            
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Gerar versão do modelo
            self.model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Salvar modelo
            await self._save_model()
            
            # Calcular métricas
            metrics = {
                'accuracy': accuracy,
                'precision_macro': 0.0,  # Implementar cálculo detalhado
                'recall_macro': 0.0,
                'f1_macro': 0.0,
                'data_treinamento': datetime.now()
            }
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Treinamento concluído em {training_time:.2f}s")
            logger.info(f"Acurácia: {accuracy:.4f}")
            
            return {
                'modelo_versao': self.model_version,
                'metricas': metrics,
                'tempo_treinamento': training_time,
                'registros_treinamento': len(X_train),
                'registros_teste': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            raise
    
    async def _load_training_data(self, db_manager, municipios: Optional[List[str]] = None) -> pd.DataFrame:
        """Carrega dados de treinamento do banco."""
        try:
            # Por enquanto, carregar dados do CSV diretamente
            # Em produção, isso viria do banco de dados
            data_path = "../../data/raw/malaria_bie_expanded.csv"
            
            if not os.path.exists(data_path):
                # Fallback para o dataset original
                data_path = "../../data/raw/malaria_bie.csv"
            
            df = pd.read_csv(data_path)
            
            # Filtrar por municípios se especificado
            if municipios:
                df = df[df['municipio'].isin(municipios)]
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepara features para treinamento."""
        try:
            # Features básicas
            feature_cols = [
                'chuva_mm', 'temp_media_c', 'temp_min_c', 'temp_max_c',
                'umidade_relativa', 'casos_lag1', 'casos_lag2', 'casos_lag3',
                'casos_lag4', 'casos_media_2s', 'casos_media_4s'
            ]
            
            # Filtrar colunas existentes
            available_cols = [col for col in feature_cols if col in df.columns]
            
            # Adicionar features temporais
            if 'ano_semana' in df.columns:
                df['ano'] = df['ano_semana'].str.split('-').str[0].astype(int)
                df['semana'] = df['ano_semana'].str.split('-').str[1].astype(int)
                available_cols.extend(['ano', 'semana'])
            
            # Preparar X
            X = df[available_cols].fillna(0)
            self.feature_columns = available_cols
            
            # Preparar y (classe de risco)
            if 'classe_risco' in df.columns:
                y = df['classe_risco']
            else:
                # Criar classes baseadas nos casos
                y = pd.cut(df['casos'], bins=3, labels=['baixo', 'medio', 'alto'])
            
            return X, y
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            raise
    
    async def _save_model(self):
        """Salva o modelo treinado."""
        try:
            model_dir = "../ml/core/models"
            os.makedirs(model_dir, exist_ok=True)
            
            # Salvar modelo
            model_path = os.path.join(model_dir, "malaria_risk_model_backend.pkl")
            joblib.dump(self.model, model_path)
            
            # Salvar metadados
            metadata = {
                'model_version': self.model_version,
                'feature_columns': self.feature_columns,
                'trained_at': datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(model_dir, "model_metadata_backend.json")
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Modelo salvo em {model_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
            raise
