"""
Módulo para treinamento e avaliação do modelo de previsão de malária.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
import joblib
from datetime import datetime
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class MalariaModel:
    """Classe para treinamento e predição do modelo de malária."""
    
    def __init__(self, model_type: str = 'random_forest', random_state: int = 42):
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.metrics = {}
        self.model_version = None
        
    def _create_model(self) -> Any:
        """Cria o modelo baseado no tipo especificado."""
        if self.model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=self.random_state,
                n_jobs=-1
            )
        elif self.model_type == 'logistic_regression':
            return LogisticRegression(
                random_state=self.random_state,
                max_iter=1000,
                multi_class='ovr'
            )
        else:
            raise ValueError(f"Tipo de modelo não suportado: {self.model_type}")
    
    def _get_param_grid(self) -> Dict:
        """Retorna grid de parâmetros para otimização."""
        if self.model_type == 'random_forest':
            return {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif self.model_type == 'logistic_regression':
            return {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        else:
            return {}
    
    def prepare_data(self, df: pd.DataFrame, target_column: str = 'risco_futuro') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara dados para treinamento.
        
        Args:
            df: DataFrame com features
            target_column: Nome da coluna target
            
        Returns:
            Tuple com (X, y) preparados
        """
        # Selecionar features numéricas
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        feature_columns = [col for col in numeric_columns if col != target_column]
        
        X = df[feature_columns].copy()
        y = df[target_column].copy()
        
        # Imputar valores ausentes
        X = X.fillna(X.mean())
        
        # Codificar target se necessário
        if y.dtype == 'object':
            y = self.label_encoder.fit_transform(y)
        
        self.feature_columns = feature_columns
        logger.info(f"Dados preparados: {len(X)} amostras, {len(feature_columns)} features")
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, 
              test_size: float = 0.2, cv_folds: int = 5) -> Dict:
        """
        Treina o modelo com validação cruzada.
        
        Args:
            X: Features de treinamento
            y: Target de treinamento
            test_size: Proporção de dados para teste
            cv_folds: Número de folds para validação cruzada
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info(f"Iniciando treinamento do modelo {self.model_type}")
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        
        # Escalar features se necessário
        if self.model_type == 'logistic_regression':
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
        else:
            X_train_scaled = X_train
            X_test_scaled = X_test
        
        # Configurar validação cruzada
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # Grid search para otimização de hiperparâmetros
        param_grid = self._get_param_grid()
        
        if param_grid:
            grid_search = GridSearchCV(
                self._create_model(),
                param_grid,
                cv=cv,
                scoring='f1_macro',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            self.model = grid_search.best_estimator_
            logger.info(f"Melhores parâmetros: {grid_search.best_params_}")
        else:
            self.model = self._create_model()
            self.model.fit(X_train_scaled, y_train)
        
        # Predições
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)
        
        # Calcular métricas
        metrics = self._calculate_metrics(y_test, y_pred, y_pred_proba)
        
        # Adicionar informações do modelo
        metrics['model_type'] = self.model_type
        metrics['model_version'] = self._generate_version()
        metrics['feature_count'] = len(self.feature_columns)
        metrics['training_samples'] = len(X_train)
        metrics['test_samples'] = len(X_test)
        
        self.metrics = metrics
        self.model_version = metrics['model_version']
        
        logger.info(f"Treinamento concluído. Acurácia: {metrics['accuracy']:.4f}")
        
        return metrics
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                          y_pred_proba: np.ndarray) -> Dict:
        """Calcula métricas de avaliação."""
        # Métricas gerais
        accuracy = accuracy_score(y_true, y_pred)
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
        
        # Métricas por classe
        precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
        
        # AUC (se binário ou multiclasse)
        try:
            if len(np.unique(y_true)) == 2:
                auc = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:
                auc = roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average='macro')
        except:
            auc = None
        
        # Matriz de confusão
        cm = confusion_matrix(y_true, y_pred)
        
        # Relatório de classificação
        class_report = classification_report(y_true, y_pred, output_dict=True)
        
        # Nomes das classes
        if hasattr(self.label_encoder, 'classes_'):
            class_names = self.label_encoder.classes_
        else:
            class_names = [f'classe_{i}' for i in range(len(np.unique(y_true)))]
        
        metrics = {
            'accuracy': accuracy,
            'precision_macro': precision_macro,
            'recall_macro': recall_macro,
            'f1_macro': f1_macro,
            'auc': auc,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'class_names': class_names.tolist() if hasattr(class_names, 'tolist') else class_names,
            'precision_baixo': precision_per_class[0] if len(precision_per_class) > 0 else None,
            'recall_baixo': recall_per_class[0] if len(recall_per_class) > 0 else None,
            'f1_baixo': f1_per_class[0] if len(f1_per_class) > 0 else None,
            'precision_medio': precision_per_class[1] if len(precision_per_class) > 1 else None,
            'recall_medio': recall_per_class[1] if len(recall_per_class) > 1 else None,
            'f1_medio': f1_per_class[1] if len(f1_per_class) > 1 else None,
            'precision_alto': precision_per_class[2] if len(precision_per_class) > 2 else None,
            'recall_alto': recall_per_class[2] if len(recall_per_class) > 2 else None,
            'f1_alto': f1_per_class[2] if len(f1_per_class) > 2 else None,
        }
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Faz predições com o modelo treinado.
        
        Args:
            X: Features para predição
            
        Returns:
            Tuple com (predições, probabilidades)
        """
        if self.model is None:
            raise ValueError("Modelo não foi treinado ainda")
        
        # Preparar features
        X_processed = X[self.feature_columns].copy()
        X_processed = X_processed.fillna(X_processed.mean())
        
        # Escalar se necessário
        if self.scaler is not None:
            X_processed = self.scaler.transform(X_processed)
        
        # Predições
        y_pred = self.model.predict(X_processed)
        y_pred_proba = self.model.predict_proba(X_processed)
        
        # Decodificar classes se necessário
        if hasattr(self.label_encoder, 'classes_'):
            y_pred = self.label_encoder.inverse_transform(y_pred)
        
        return y_pred, y_pred_proba
    
    def predict_risk_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Calcula score de risco (probabilidade da classe 'alto').
        
        Args:
            X: Features para predição
            
        Returns:
            Array com scores de risco
        """
        _, y_pred_proba = self.predict(X)
        
        # Se há 3 classes, retornar probabilidade da classe 'alto' (índice 2)
        if y_pred_proba.shape[1] == 3:
            return y_pred_proba[:, 2]
        else:
            # Se binário, retornar probabilidade da classe positiva
            return y_pred_proba[:, 1] if y_pred_proba.shape[1] == 2 else y_pred_proba[:, 0]
    
    def save_model(self, filepath: str) -> bool:
        """
        Salva o modelo treinado.
        
        Args:
            filepath: Caminho para salvar o modelo
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_columns': self.feature_columns,
                'model_type': self.model_type,
                'model_version': self.model_version,
                'metrics': self.metrics,
                'created_at': datetime.now().isoformat()
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Modelo salvo: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Carrega um modelo salvo.
        
        Args:
            filepath: Caminho do modelo salvo
            
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data.get('scaler')
            self.label_encoder = model_data['label_encoder']
            self.feature_columns = model_data['feature_columns']
            self.model_type = model_data['model_type']
            self.model_version = model_data.get('model_version')
            self.metrics = model_data.get('metrics', {})
            
            logger.info(f"Modelo carregado: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def _generate_version(self) -> str:
        """Gera versão do modelo baseada na data/hora."""
        return datetime.now().strftime("v%Y%m%d_%H%M%S")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retorna importância das features (apenas para Random Forest).
        
        Returns:
            DataFrame com importância das features
        """
        if self.model_type != 'random_forest' or self.model is None:
            return pd.DataFrame()
        
        try:
            importance = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            return feature_importance
        except Exception as e:
            logger.error(f"Erro ao obter importância das features: {e}")
            return pd.DataFrame()


def train_malaria_model(df: pd.DataFrame, 
                       model_type: str = 'random_forest',
                       save_path: str = 'models/malaria_model.joblib') -> MalariaModel:
    """
    Função utilitária para treinar modelo de malária.
    
    Args:
        df: DataFrame com dados de treinamento
        model_type: Tipo do modelo ('random_forest' ou 'logistic_regression')
        save_path: Caminho para salvar o modelo
        
    Returns:
        Modelo treinado
    """
    # Criar diretório se não existir
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Criar e treinar modelo
    model = MalariaModel(model_type=model_type)
    
    # Preparar dados
    X, y = model.prepare_data(df)
    
    # Treinar
    metrics = model.train(X, y)
    
    # Salvar modelo
    model.save_model(save_path)
    
    logger.info(f"Modelo treinado e salvo: {save_path}")
    logger.info(f"Métricas: Acurácia={metrics['accuracy']:.4f}, F1={metrics['f1_macro']:.4f}")
    
    return model


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar dados de exemplo
    from src.features.feature_engineering import create_sample_features_data
    
    df = create_sample_features_data()
    print(f"Dados de exemplo: {len(df)} registros")
    
    # Treinar modelo
    model = train_malaria_model(df, model_type='random_forest')
    
    # Mostrar importância das features
    importance = model.get_feature_importance()
    print("\nImportância das features:")
    print(importance.head(10))
