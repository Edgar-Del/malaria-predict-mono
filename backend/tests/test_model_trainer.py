"""
Testes para o módulo de treinamento do modelo.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime

from src.model.trainer import ModelTrainer


class TestModelTrainer:
    """Testes para a classe ModelTrainer."""
    
    def test_init(self):
        """Testa inicialização do ModelTrainer."""
        trainer = ModelTrainer()
        
        assert trainer.model_path is not None
        assert trainer.random_state == 42
        assert trainer.model is None
        assert trainer.feature_engineer is not None
    
    def test_init_with_custom_path(self):
        """Testa inicialização com caminho customizado."""
        custom_path = "custom/path/model.joblib"
        trainer = ModelTrainer(model_path=custom_path)
        
        assert trainer.model_path == custom_path
    
    def test_create_model_random_forest(self):
        """Testa criação de modelo Random Forest."""
        trainer = ModelTrainer()
        model = trainer.create_model('random_forest')
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
    
    def test_create_model_invalid_type(self):
        """Testa criação de modelo com tipo inválido."""
        trainer = ModelTrainer()
        
        with pytest.raises(ValueError):
            trainer.create_model('invalid_type')
    
    def test_prepare_training_data(self, sample_features_data):
        """Testa preparação de dados para treinamento."""
        trainer = ModelTrainer()
        
        # Adicionar classe_risco aos dados
        sample_features_data['classe_risco'] = ['baixo', 'medio', 'alto']
        
        X, y = trainer.prepare_training_data(sample_features_data)
        
        # Verificar se X e y têm o mesmo número de amostras
        assert len(X) == len(y)
        
        # Verificar se X contém apenas features numéricas
        assert X.select_dtypes(include=[np.number]).shape[1] == X.shape[1]
        
        # Verificar se y contém apenas valores numéricos
        assert pd.api.types.is_numeric_dtype(y)
    
    def test_evaluate_model(self, mock_model, mock_label_encoder):
        """Testa avaliação do modelo."""
        trainer = ModelTrainer()
        trainer.model = mock_model
        trainer.label_encoder = mock_label_encoder
        
        # Criar dados de teste
        X_test = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        y_test = np.array([0, 1, 2])  # baixo, medio, alto
        
        # Avaliar modelo
        metrics = trainer.evaluate_model(X_test, y_test)
        
        # Verificar se métricas foram calculadas
        assert 'accuracy' in metrics
        assert 'precision_macro' in metrics
        assert 'recall_macro' in metrics
        assert 'f1_macro' in metrics
        
        # Verificar se métricas estão no range correto
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision_macro'] <= 1
        assert 0 <= metrics['recall_macro'] <= 1
        assert 0 <= metrics['f1_macro'] <= 1
    
    def test_get_feature_importance(self, mock_model):
        """Testa obtenção de importância das features."""
        trainer = ModelTrainer()
        trainer.model = mock_model
        trainer.feature_names = ['feature1', 'feature2', 'feature3', 'feature4',
                                'feature5', 'feature6', 'feature7', 'feature8']
        
        importance = trainer.get_feature_importance()
        
        # Verificar se retorna dicionário
        assert isinstance(importance, dict)
        
        # Verificar se todas as features estão presentes
        assert len(importance) == len(trainer.feature_names)
        
        # Verificar se valores são numéricos
        assert all(isinstance(v, (int, float)) for v in importance.values())
    
    def test_save_model(self, mock_model, mock_label_encoder):
        """Testa salvamento do modelo."""
        trainer = ModelTrainer()
        trainer.model = mock_model
        trainer.label_encoder = mock_label_encoder
        trainer.feature_names = ['feature1', 'feature2']
        trainer.model_version = "v1.0.0"
        
        # Mock do joblib.dump
        with patch('src.model.trainer.joblib.dump') as mock_dump:
            trainer.save_model()
            
            # Verificar se joblib.dump foi chamado
            mock_dump.assert_called_once()
            
            # Verificar se dados salvos contêm componentes esperados
            call_args = mock_dump.call_args[0][0]
            assert 'model' in call_args
            assert 'label_encoder' in call_args
            assert 'feature_names' in call_args
            assert 'model_version' in call_args
    
    def test_load_model_success(self, mock_model, mock_label_encoder):
        """Testa carregamento bem-sucedido do modelo."""
        trainer = ModelTrainer()
        
        # Mock do joblib.load
        mock_data = {
            'model': mock_model,
            'label_encoder': mock_label_encoder,
            'feature_names': ['feature1', 'feature2'],
            'model_version': 'v1.0.0'
        }
        
        with patch('src.model.trainer.joblib.load', return_value=mock_data), \
             patch('src.model.trainer.os.path.exists', return_value=True):
            
            success = trainer.load_model()
            
            assert success == True
            assert trainer.model == mock_model
            assert trainer.label_encoder == mock_label_encoder
            assert trainer.feature_names == ['feature1', 'feature2']
            assert trainer.model_version == 'v1.0.0'
    
    def test_load_model_file_not_found(self):
        """Testa carregamento quando arquivo não existe."""
        trainer = ModelTrainer()
        
        with patch('src.model.trainer.os.path.exists', return_value=False):
            success = trainer.load_model()
            
            assert success == False
            assert trainer.model is None
    
    def test_load_model_error(self):
        """Testa erro no carregamento do modelo."""
        trainer = ModelTrainer()
        
        with patch('src.model.trainer.os.path.exists', return_value=True), \
             patch('src.model.trainer.joblib.load', side_effect=Exception("Erro")):
            
            success = trainer.load_model()
            
            assert success == False
    
    def test_save_metrics_to_db(self, mock_database_manager):
        """Testa salvamento de métricas no banco."""
        trainer = ModelTrainer()
        trainer.model_version = "v1.0.0"
        trainer.model = Mock()
        trainer.model.n_estimators = 100
        trainer.model.max_depth = 10
        
        metrics = {
            'accuracy': 0.85,
            'precision_macro': 0.82,
            'recall_macro': 0.83,
            'f1_macro': 0.825
        }
        
        success = trainer.save_metrics_to_db(mock_database_manager, metrics, 'RandomForest')
        
        # Verificar se insert_metricas foi chamado
        mock_database_manager.insert_metricas.assert_called_once()
        
        # Verificar se métricas foram salvas
        call_args = mock_database_manager.insert_metricas.call_args[0][0]
        assert call_args['modelo_versao'] == "v1.0.0"
        assert call_args['accuracy'] == 0.85
    
    def test_cross_validate(self, mock_model):
        """Testa validação cruzada."""
        trainer = ModelTrainer()
        trainer.model = mock_model
        
        # Criar dados de teste
        X = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [6, 7, 8, 9, 10]
        })
        y = np.array([0, 1, 0, 1, 0])
        
        # Mock do cross_val_score
        with patch('src.model.trainer.cross_val_score', return_value=np.array([0.8, 0.85, 0.82, 0.88, 0.83])):
            results = trainer.cross_validate(X, y, cv_folds=5)
            
            # Verificar se resultados foram calculados
            assert 'cv_mean' in results
            assert 'cv_std' in results
            assert 'cv_scores' in results
            
            # Verificar se valores estão corretos
            assert results['cv_mean'] == 0.836
            assert results['cv_std'] == 0.028
            assert len(results['cv_scores']) == 5
    
    def test_get_model_info_no_model(self):
        """Testa informações do modelo quando não há modelo carregado."""
        trainer = ModelTrainer()
        
        info = trainer.get_model_info()
        
        assert info['status'] == 'no_model'
    
    def test_get_model_info_with_model(self, mock_model, mock_label_encoder):
        """Testa informações do modelo quando há modelo carregado."""
        trainer = ModelTrainer()
        trainer.model = mock_model
        trainer.label_encoder = mock_label_encoder
        trainer.feature_names = ['feature1', 'feature2']
        trainer.model_version = "v1.0.0"
        
        info = trainer.get_model_info()
        
        assert info['status'] == 'loaded'
        assert info['model_version'] == "v1.0.0"
        assert info['feature_count'] == 2
        assert 'classes' in info


class TestModelTrainerIntegration:
    """Testes de integração para ModelTrainer."""
    
    @patch('src.model.trainer.FeatureEngineer')
    def test_train_model_success(self, mock_feature_engineer, mock_database_manager):
        """Testa treinamento bem-sucedido do modelo."""
        # Configurar mocks
        mock_engineer_instance = Mock()
        mock_engineer_instance.engineer_features.return_value = pd.DataFrame({
            'municipio': ['Kuito', 'Camacupa'],
            'ano_semana': ['2024-01', '2024-02'],
            'casos': [10, 15],
            'classe_risco': ['baixo', 'medio']
        })
        mock_engineer_instance.prepare_training_data.return_value = (
            pd.DataFrame({'feature1': [1, 2], 'feature2': [3, 4]}),
            np.array([0, 1])
        )
        mock_feature_engineer.return_value = mock_engineer_instance
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = np.array([0, 1])
        mock_model.predict_proba.return_value = np.array([[0.8, 0.2], [0.3, 0.7]])
        
        with patch('src.model.trainer.ModelTrainer.create_model', return_value=mock_model), \
             patch('src.model.trainer.ModelTrainer.evaluate_model', return_value={'accuracy': 0.85}), \
             patch('src.model.trainer.ModelTrainer.save_model'), \
             patch('src.model.trainer.ModelTrainer.save_metrics_to_db'):
            
            trainer = ModelTrainer()
            result = trainer.train_model(mock_database_manager)
            
            # Verificar se treinamento foi bem-sucedido
            assert result['status'] == 'success'
            assert 'modelo_versao' in result
            assert 'metricas' in result
            assert 'tempo_treinamento' in result
    
    def test_train_model_no_data(self, mock_database_manager):
        """Testa treinamento quando não há dados."""
        # Mock do get_series_semanais retornando DataFrame vazio
        mock_database_manager.get_series_semanais.return_value = pd.DataFrame()
        
        trainer = ModelTrainer()
        
        with pytest.raises(ValueError, match="Nenhum dado de treinamento encontrado"):
            trainer.train_model(mock_database_manager)
    
    def test_train_model_retreinar_existing(self, mock_database_manager):
        """Testa retreinamento quando modelo já existe."""
        # Mock do get_metricas_latest retornando métricas existentes
        mock_database_manager.get_metricas_latest.return_value = {'modelo_versao': 'v1.0.0'}
        
        trainer = ModelTrainer()
        
        with pytest.raises(Exception):  # Deve falhar se retreinar=False
            trainer.train_model(mock_database_manager, retreinar=False)

