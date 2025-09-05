"""
Módulo de treinamento do modelo de previsão de risco de malária.
"""

import os
import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

from ..features.feature_engineering import FeatureEngineer
from ..ingest.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Classe para treinamento do modelo de previsão de malária."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv('MODEL_PATH', 'models/malaria_model.joblib')
        self.random_state = int(os.getenv('RANDOM_STATE', 42))
        
        # Criar diretório de modelos se não existir
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.model_version = None
        
    def load_training_data(self, db_manager: DatabaseManager, 
                          municipios: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Carrega dados de treinamento do banco de dados.
        
        Args:
            db_manager: Gerenciador do banco de dados
            municipios: Lista de municípios para treinar (opcional)
            
        Returns:
            DataFrame com dados de treinamento
        """
        logger.info("Carregando dados de treinamento")
        
        # Obter dados das séries semanais
        df = db_manager.get_series_semanais()
        
        if df.empty:
            raise ValueError("Nenhum dado de treinamento encontrado")
        
        # Filtrar por municípios se especificado
        if municipios:
            df = df[df['municipio_nome'].isin(municipios)]
            logger.info(f"Dados filtrados para municípios: {municipios}")
        
        # Renomear coluna para compatibilidade
        df = df.rename(columns={'municipio_nome': 'municipio'})
        
        logger.info(f"Dados carregados: {len(df)} registros")
        return df
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara dados para treinamento.
        
        Args:
            df: DataFrame com dados brutos
            
        Returns:
            Tupla com (X, y) para treinamento
        """
        logger.info("Preparando dados para treinamento")
        
        # Aplicar engenharia de features
        df_features = self.feature_engineer.engineer_features(df)
        
        # Preparar dados de treinamento
        X, y = self.feature_engineer.prepare_training_data(df_features)
        
        # Codificar labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Salvar nomes das features
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")
        logger.info(f"Classes: {self.label_encoder.classes_}")
        
        return X, y_encoded
    
    def create_model(self, model_type: str = 'random_forest') -> Any:
        """
        Cria instância do modelo.
        
        Args:
            model_type: Tipo do modelo ('random_forest', 'gradient_boosting', 'svm')
            
        Returns:
            Instância do modelo
        """
        if model_type == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Tipo de modelo não suportado: {model_type}")
        
        logger.info(f"Modelo criado: {model_type}")
        return model
    
    def hyperparameter_tuning(self, X: pd.DataFrame, y: np.ndarray, 
                             model_type: str = 'random_forest') -> Any:
        """
        Realiza ajuste de hiperparâmetros.
        
        Args:
            X: Features de treinamento
            y: Labels de treinamento
            model_type: Tipo do modelo
            
        Returns:
            Melhor modelo encontrado
        """
        logger.info("Iniciando ajuste de hiperparâmetros")
        
        if model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            base_model = RandomForestClassifier(random_state=self.random_state, n_jobs=-1)
            
        else:
            raise ValueError(f"Tipo de modelo não suportado: {model_type}")
        
        # Grid search com validação cruzada
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=5,
            scoring='f1_macro',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        logger.info(f"Melhores parâmetros: {grid_search.best_params_}")
        logger.info(f"Melhor score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def train_model(self, db_manager: DatabaseManager,
                   municipios: Optional[List[str]] = None,
                   test_size: float = 0.2,
                   random_state: Optional[int] = None,
                   use_hyperparameter_tuning: bool = False,
                   model_type: str = 'random_forest') -> Dict[str, Any]:
        """
        Treina o modelo de previsão de malária.
        
        Args:
            db_manager: Gerenciador do banco de dados
            municipios: Lista de municípios para treinar
            test_size: Proporção de dados para teste
            random_state: Seed para reprodutibilidade
            use_hyperparameter_tuning: Se deve usar ajuste de hiperparâmetros
            model_type: Tipo do modelo
            
        Returns:
            Dicionário com resultados do treinamento
        """
        start_time = datetime.now()
        
        try:
            # Carregar dados
            df = self.load_training_data(db_manager, municipios)
            
            # Preparar dados
            X, y = self.prepare_training_data(df)
            
            # Dividir dados
            if random_state is None:
                random_state = self.random_state
                
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, 
                stratify=y
            )
            
            logger.info(f"Dados divididos: {len(X_train)} treino, {len(X_test)} teste")
            
            # Criar ou ajustar modelo
            if use_hyperparameter_tuning:
                self.model = self.hyperparameter_tuning(X_train, y_train, model_type)
            else:
                self.model = self.create_model(model_type)
            
            # Treinar modelo
            logger.info("Iniciando treinamento do modelo")
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            metrics = self.evaluate_model(X_test, y_test)
            
            # Gerar versão do modelo
            self.model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Salvar modelo
            self.save_model()
            
            # Salvar métricas no banco
            self.save_metrics_to_db(db_manager, metrics, model_type)
            
            # Calcular tempo de treinamento
            training_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Treinamento concluído em {training_time:.2f} segundos")
            
            return {
                'status': 'success',
                'modelo_versao': self.model_version,
                'metricas': metrics,
                'tempo_treinamento': training_time,
                'registros_treinamento': len(X_train),
                'registros_teste': len(X_test),
                'feature_importance': self.get_feature_importance()
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            raise
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict[str, float]:
        """
        Avalia o modelo treinado.
        
        Args:
            X_test: Features de teste
            y_test: Labels de teste
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info("Avaliando modelo")
        
        # Predições
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Métricas gerais
        accuracy = accuracy_score(y_test, y_pred)
        precision_macro = precision_score(y_test, y_pred, average='macro')
        recall_macro = recall_score(y_test, y_pred, average='macro')
        f1_macro = f1_score(y_test, y_pred, average='macro')
        
        # Métricas por classe
        classes = self.label_encoder.classes_
        precision_per_class = precision_score(y_test, y_pred, average=None)
        recall_per_class = recall_score(y_test, y_pred, average=None)
        f1_per_class = f1_score(y_test, y_pred, average=None)
        
        # Criar dicionário de métricas
        metrics = {
            'accuracy': accuracy,
            'precision_macro': precision_macro,
            'recall_macro': recall_macro,
            'f1_macro': f1_macro
        }
        
        # Adicionar métricas por classe
        for i, class_name in enumerate(classes):
            metrics[f'precision_{class_name}'] = precision_per_class[i]
            metrics[f'recall_{class_name}'] = recall_per_class[i]
            metrics[f'f1_{class_name}'] = f1_per_class[i]
        
        # Log das métricas
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"F1 Macro: {f1_macro:.4f}")
        
        for i, class_name in enumerate(classes):
            logger.info(f"{class_name} - Precision: {precision_per_class[i]:.4f}, "
                       f"Recall: {recall_per_class[i]:.4f}, F1: {f1_per_class[i]:.4f}")
        
        return metrics
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Obtém importância das features.
        
        Returns:
            Dicionário com importância das features
        """
        if self.model is None:
            return {}
        
        return self.feature_engineer.get_feature_importance(
            self.model, self.feature_names
        )
    
    def save_model(self) -> None:
        """
        Salva o modelo treinado.
        """
        if self.model is None:
            raise ValueError("Modelo não foi treinado")
        
        # Criar dicionário com todos os componentes
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'model_version': self.model_version,
            'training_date': datetime.now().isoformat()
        }
        
        # Salvar modelo
        joblib.dump(model_data, self.model_path)
        logger.info(f"Modelo salvo: {self.model_path}")
    
    def load_model(self) -> bool:
        """
        Carrega modelo salvo.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Arquivo de modelo não encontrado: {self.model_path}")
                return False
            
            model_data = joblib.load(self.model_path)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('model_version', 'unknown')
            
            logger.info(f"Modelo carregado: {self.model_path}")
            logger.info(f"Versão: {self.model_version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def save_metrics_to_db(self, db_manager: DatabaseManager, 
                          metrics: Dict[str, float], model_type: str) -> None:
        """
        Salva métricas no banco de dados.
        
        Args:
            db_manager: Gerenciador do banco de dados
            metrics: Métricas do modelo
            model_type: Tipo do modelo
        """
        try:
            # Preparar dados das métricas
            metricas_data = {
                'modelo_versao': self.model_version,
                'modelo_tipo': model_type,
                'data_treinamento': datetime.now(),
                'parametros': {
                    'n_estimators': getattr(self.model, 'n_estimators', None),
                    'max_depth': getattr(self.model, 'max_depth', None),
                    'min_samples_split': getattr(self.model, 'min_samples_split', None),
                    'min_samples_leaf': getattr(self.model, 'min_samples_leaf', None),
                    'random_state': self.random_state
                }
            }
            
            # Adicionar métricas
            metricas_data.update(metrics)
            
            # Salvar no banco
            success = db_manager.insert_metricas(metricas_data)
            
            if success:
                logger.info("Métricas salvas no banco de dados")
            else:
                logger.warning("Erro ao salvar métricas no banco")
                
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
    
    def cross_validate(self, X: pd.DataFrame, y: np.ndarray, 
                      cv_folds: int = 5) -> Dict[str, float]:
        """
        Realiza validação cruzada do modelo.
        
        Args:
            X: Features
            y: Labels
            cv_folds: Número de folds para validação cruzada
            
        Returns:
            Dicionário com scores de validação cruzada
        """
        if self.model is None:
            raise ValueError("Modelo não foi criado")
        
        logger.info(f"Realizando validação cruzada com {cv_folds} folds")
        
        # Validação cruzada
        cv_scores = cross_val_score(
            self.model, X, y, cv=cv_folds, scoring='f1_macro'
        )
        
        results = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_scores': cv_scores.tolist()
        }
        
        logger.info(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o modelo atual.
        
        Returns:
            Dicionário com informações do modelo
        """
        if self.model is None:
            return {'status': 'no_model'}
        
        return {
            'status': 'loaded',
            'model_version': self.model_version,
            'model_type': type(self.model).__name__,
            'feature_count': len(self.feature_names),
            'classes': self.label_encoder.classes_.tolist(),
            'model_path': self.model_path
        }


def train_sample_model() -> None:
    """
    Função para treinar modelo com dados de exemplo.
    """
    from ..ingest.data_loader import create_sample_data
    from ..ingest.database_manager import DatabaseManager
    import tempfile
    import os
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Criar dados de exemplo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            create_sample_data(tmp.name)
            temp_path = tmp.name
        
        # Carregar dados
        from ..ingest.data_loader import DataLoader
        loader = DataLoader()
        df = loader.load_and_process_data(os.path.basename(temp_path))
        
        # Simular banco de dados
        class MockDB:
            def get_series_semanais(self):
                return df.rename(columns={'municipio': 'municipio_nome'})
            
            def insert_metricas(self, data):
                print(f"Métricas simuladas: {data}")
                return True
        
        # Treinar modelo
        trainer = ModelTrainer()
        db_mock = MockDB()
        
        resultado = trainer.train_model(db_mock)
        
        print("Treinamento concluído com sucesso!")
        print(f"Versão do modelo: {resultado['modelo_versao']}")
        print(f"Métricas: {resultado['metricas']}")
        
    finally:
        # Limpar arquivo temporário
        if 'temp_path' in locals():
            os.unlink(temp_path)


if __name__ == "__main__":
    train_sample_model()

