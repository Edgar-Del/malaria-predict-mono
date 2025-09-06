"""
Testes para o módulo de modelagem de malária.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import os

from src.model.malaria_model import MalariaModel, train_malaria_model


class TestMalariaModel:
    """Testes para a classe MalariaModel."""
    
    def test_init(self):
        """Testa inicialização do modelo."""
        model = MalariaModel(model_type='random_forest', random_state=42)
        assert model.model_type == 'random_forest'
        assert model.random_state == 42
        assert model.model is None
        assert model.scaler is None
        assert model.feature_columns == []
        assert model.metrics == {}
        assert model.model_version is None
    
    def test_create_model_random_forest(self):
        """Testa criação de modelo Random Forest."""
        model = MalariaModel(model_type='random_forest')
        rf_model = model._create_model()
        
        assert hasattr(rf_model, 'fit')
        assert hasattr(rf_model, 'predict')
        assert hasattr(rf_model, 'predict_proba')
    
    def test_create_model_logistic_regression(self):
        """Testa criação de modelo Logistic Regression."""
        model = MalariaModel(model_type='logistic_regression')
        lr_model = model._create_model()
        
        assert hasattr(lr_model, 'fit')
        assert hasattr(lr_model, 'predict')
        assert hasattr(lr_model, 'predict_proba')
    
    def test_create_model_invalid_type(self):
        """Testa criação de modelo com tipo inválido."""
        model = MalariaModel(model_type='invalid_type')
        
        with pytest.raises(ValueError):
            model._create_model()
    
    def test_get_param_grid_random_forest(self):
        """Testa grid de parâmetros para Random Forest."""
        model = MalariaModel(model_type='random_forest')
        param_grid = model._get_param_grid()
        
        assert 'n_estimators' in param_grid
        assert 'max_depth' in param_grid
        assert 'min_samples_split' in param_grid
        assert 'min_samples_leaf' in param_grid
    
    def test_get_param_grid_logistic_regression(self):
        """Testa grid de parâmetros para Logistic Regression."""
        model = MalariaModel(model_type='logistic_regression')
        param_grid = model._get_param_grid()
        
        assert 'C' in param_grid
        assert 'penalty' in param_grid
        assert 'solver' in param_grid
    
    def test_prepare_data(self, sample_weekly_data, feature_engineer):
        """Testa preparação de dados."""
        model = MalariaModel()
        
        # Criar features
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        
        # Preparar dados
        X, y = model.prepare_data(df_with_features)
        
        # Verificações
        assert len(X) == len(y)
        assert len(model.feature_columns) > 0
        assert not X.isnull().any().any()
        assert not y.isnull().any()
        
        # Verificar se target foi codificado se necessário
        if y.dtype == 'object':
            assert hasattr(model.label_encoder, 'classes_')
    
    def test_train_model(self, sample_weekly_data, feature_engineer, temp_model_path):
        """Testa treinamento do modelo."""
        model = MalariaModel(model_type='random_forest', random_state=42)
        
        # Criar features
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        
        # Preparar dados
        X, y = model.prepare_data(df_with_features)
        
        # Treinar modelo
        metrics = model.train(X, y, test_size=0.3, cv_folds=3)
        
        # Verificações
        assert model.model is not None
        assert model.model_version is not None
        assert len(metrics) > 0
        
        # Verificar métricas essenciais
        required_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
        for metric in required_metrics:
            assert metric in metrics
            assert 0 <= metrics[metric] <= 1
        
        # Verificar se modelo foi salvo
        model.save_model(temp_model_path)
        assert os.path.exists(temp_model_path)
    
    def test_predict(self, sample_weekly_data, feature_engineer, temp_model_path):
        """Testa predição com modelo treinado."""
        model = MalariaModel(model_type='random_forest', random_state=42)
        
        # Criar features e treinar
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        X, y = model.prepare_data(df_with_features)
        model.train(X, y, test_size=0.3, cv_folds=3)
        
        # Fazer predições
        y_pred, y_pred_proba = model.predict(X)
        
        # Verificações
        assert len(y_pred) == len(X)
        assert len(y_pred_proba) == len(X)
        assert y_pred_proba.shape[1] > 0  # Deve ter probabilidades para cada classe
        
        # Verificar se probabilidades somam 1
        prob_sums = y_pred_proba.sum(axis=1)
        assert np.allclose(prob_sums, 1.0, atol=1e-6)
    
    def test_predict_risk_score(self, sample_weekly_data, feature_engineer):
        """Testa cálculo de score de risco."""
        model = MalariaModel(model_type='random_forest', random_state=42)
        
        # Criar features e treinar
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        X, y = model.prepare_data(df_with_features)
        model.train(X, y, test_size=0.3, cv_folds=3)
        
        # Calcular scores de risco
        risk_scores = model.predict_risk_score(X)
        
        # Verificações
        assert len(risk_scores) == len(X)
        assert all(0 <= score <= 1 for score in risk_scores)
    
    def test_save_and_load_model(self, sample_weekly_data, feature_engineer, temp_model_path):
        """Testa salvamento e carregamento de modelo."""
        # Treinar e salvar modelo
        model1 = MalariaModel(model_type='random_forest', random_state=42)
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        X, y = model1.prepare_data(df_with_features)
        model1.train(X, y, test_size=0.3, cv_folds=3)
        model1.save_model(temp_model_path)
        
        # Carregar modelo
        model2 = MalariaModel()
        success = model2.load_model(temp_model_path)
        
        # Verificações
        assert success
        assert model2.model is not None
        assert model2.model_type == model1.model_type
        assert model2.feature_columns == model1.feature_columns
        assert model2.model_version == model1.model_version
        
        # Verificar se predições são iguais
        y_pred1, _ = model1.predict(X)
        y_pred2, _ = model2.predict(X)
        assert np.array_equal(y_pred1, y_pred2)
    
    def test_get_feature_importance(self, sample_weekly_data, feature_engineer):
        """Testa obtenção de importância das features."""
        model = MalariaModel(model_type='random_forest', random_state=42)
        
        # Criar features e treinar
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        X, y = model.prepare_data(df_with_features)
        model.train(X, y, test_size=0.3, cv_folds=3)
        
        # Obter importância das features
        importance_df = model.get_feature_importance()
        
        # Verificações
        assert isinstance(importance_df, pd.DataFrame)
        assert 'feature' in importance_df.columns
        assert 'importance' in importance_df.columns
        assert len(importance_df) == len(model.feature_columns)
        assert all(0 <= imp <= 1 for imp in importance_df['importance'])
    
    def test_calculate_metrics(self):
        """Testa cálculo de métricas."""
        model = MalariaModel()
        
        # Dados de teste
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 1, 0, 1, 2])
        y_pred_proba = np.array([
            [0.8, 0.1, 0.1],
            [0.1, 0.8, 0.1],
            [0.1, 0.7, 0.2],
            [0.9, 0.05, 0.05],
            [0.05, 0.9, 0.05],
            [0.1, 0.1, 0.8]
        ])
        
        metrics = model._calculate_metrics(y_true, y_pred, y_pred_proba)
        
        # Verificações
        required_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
        for metric in required_metrics:
            assert metric in metrics
            assert 0 <= metrics[metric] <= 1
        
        # Verificar métricas por classe
        class_metrics = ['precision_baixo', 'recall_baixo', 'f1_baixo',
                        'precision_medio', 'recall_medio', 'f1_medio',
                        'precision_alto', 'recall_alto', 'f1_alto']
        for metric in class_metrics:
            if metrics[metric] is not None:
                assert 0 <= metrics[metric] <= 1


class TestMalariaModelIntegration:
    """Testes de integração para MalariaModel."""
    
    def test_full_training_pipeline(self, sample_weekly_data, feature_engineer, temp_model_path):
        """Testa pipeline completo de treinamento."""
        # Criar features
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        
        # Treinar modelo usando função utilitária
        model = train_malaria_model(df_with_features, 'random_forest', temp_model_path)
        
        # Verificações
        assert model.model is not None
        assert model.model_version is not None
        assert len(model.metrics) > 0
        assert os.path.exists(temp_model_path)
        
        # Verificar se modelo pode fazer predições
        X, y = model.prepare_data(df_with_features)
        y_pred, y_pred_proba = model.predict(X)
        assert len(y_pred) == len(X)
        assert len(y_pred_proba) == len(X)
    
    def test_model_persistence(self, sample_weekly_data, feature_engineer, temp_model_path):
        """Testa persistência completa do modelo."""
        # Treinar modelo
        model1 = MalariaModel(model_type='random_forest', random_state=42)
        df_with_features = feature_engineer.create_all_features(sample_weekly_data)
        X, y = model1.prepare_data(df_with_features)
        model1.train(X, y, test_size=0.3, cv_folds=3)
        model1.save_model(temp_model_path)
        
        # Carregar modelo em nova instância
        model2 = MalariaModel()
        model2.load_model(temp_model_path)
        
        # Verificar se tudo foi restaurado corretamente
        assert model2.model is not None
        assert model2.scaler == model1.scaler
        assert model2.label_encoder.classes_.tolist() == model1.label_encoder.classes_.tolist()
        assert model2.feature_columns == model1.feature_columns
        assert model2.model_type == model1.model_type
        assert model2.model_version == model1.model_version
        
        # Verificar se métricas foram restauradas
        assert model2.metrics == model1.metrics
