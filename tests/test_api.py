"""
Testes para a API FastAPI.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api.main import app
from src.api.models import PredictionResponse, TrainingResponse, MetricsResponse


class TestAPIEndpoints:
    """Testes para endpoints da API."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "ativo"
    
    def test_health_check(self, client):
        """Testa verificação de saúde."""
        response = client.get("/health")
            assert response.status_code == 200
        
            data = response.json()
        assert "status" in data
        assert "database" in data
        assert "model" in data
        assert "timestamp" in data
    
    @patch('src.api.endpoints.db_manager')
    def test_get_municipios(self, mock_db, client, sample_municipalities):
        """Testa obtenção de municípios."""
        mock_db.get_municipios.return_value = sample_municipalities
        
        response = client.get("/municipios")
        assert response.status_code == 200
        
        data = response.json()
        assert "municipios" in data
        assert "total" in data
        assert data["total"] == len(sample_municipalities)
        assert len(data["municipios"]) == len(sample_municipalities)
    
    @patch('src.api.endpoints.db_manager')
    def test_get_weekly_predictions(self, mock_db, client, sample_predictions):
        """Testa obtenção de previsões semanais."""
        mock_db.get_previsoes.return_value = sample_predictions
        
        response = client.get("/previsoes/semana/2024-01")
        assert response.status_code == 200
        
        data = response.json()
        assert "previsoes" in data
        assert "total" in data
        assert "ano_semana" in data
        assert data["ano_semana"] == "2024-01"
        assert data["total"] == len(sample_predictions)
    
    @patch('src.api.endpoints.db_manager')
    def test_get_latest_metrics(self, mock_db, client, sample_metrics):
        """Testa obtenção de métricas."""
        mock_db.get_metricas_latest.return_value = sample_metrics
        
        response = client.get("/metrics/latest")
        assert response.status_code == 200
        
        data = response.json()
        assert "modelo_versao" in data
        assert "accuracy" in data
        assert "precision_macro" in data
        assert "recall_macro" in data
        assert "f1_macro" in data
    
    @patch('src.api.endpoints.db_manager')
    def test_get_municipality_series(self, mock_db, client):
        """Testa obtenção de série temporal."""
        mock_series = [
            {
                "ano_semana": "2024-01",
                "casos": 50,
                "chuva_mm": 100.5,
                "temp_media_c": 23.0,
                "created_at": "2024-01-01T00:00:00"
            }
        ]
        mock_db.get_municipios.return_value = [{"id": 1, "nome": "Kuito"}]
        mock_db.get_series_semanais.return_value = mock_series
        
        response = client.get("/series/Kuito?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "series" in data
        assert "municipio" in data
        assert "total" in data
        assert data["municipio"] == "Kuito"
        assert len(data["series"]) == 1
    
    @patch('src.api.endpoints.db_manager')
    def test_get_municipality_series_not_found(self, mock_db, client):
        """Testa obtenção de série temporal para município não encontrado."""
        mock_db.get_municipios.return_value = []
        
        response = client.get("/series/MunicipioInexistente")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Município" in data["detail"]
    
    @patch('src.api.endpoints.db_manager')
    @patch('src.api.endpoints.feature_engineer')
    @patch('src.api.endpoints.MalariaModel')
    def test_train_model(self, mock_model_class, mock_feature_engineer, mock_db, client, sample_weekly_data):
        """Testa treinamento do modelo."""
        # Mock dos dados
        mock_db.get_series_semanais.return_value = sample_weekly_data
        
        # Mock do feature engineer
        mock_feature_engineer.create_all_features.return_value = sample_weekly_data
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.prepare_data.return_value = (sample_weekly_data[['casos']], sample_weekly_data['casos'])
        mock_model.train.return_value = {
            'model_version': 'v1.0.0',
            'accuracy': 0.85,
            'precision_macro': 0.82,
            'recall_macro': 0.83,
            'f1_macro': 0.825
        }
        mock_model.save_model.return_value = True
        mock_model_class.return_value = mock_model
        
        response = client.post("/train")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "modelo_versao" in data
        assert "metrics" in data
        assert "training_time" in data
        assert "message" in data
        assert data["status"] == "success"
    
    @patch('src.api.endpoints.db_manager')
    @patch('src.api.endpoints.feature_engineer')
    @patch('src.api.endpoints.get_malaria_model')
    def test_predict_risk(self, mock_get_model, mock_feature_engineer, mock_db, client, sample_weekly_data):
        """Testa predição de risco."""
        # Mock dos dados
        mock_db.get_series_semanais.return_value = sample_weekly_data
        
        # Mock do feature engineer
        mock_feature_engineer.create_all_features.return_value = sample_weekly_data
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.model = Mock()  # Modelo carregado
        mock_model.prepare_data.return_value = (sample_weekly_data[['casos']], sample_weekly_data['casos'])
        mock_model.predict.return_value = (['alto'], [[0.1, 0.2, 0.7]])
        mock_model.predict_risk_score.return_value = [0.85]
        mock_model.model_version = 'v1.0.0'
        mock_model.label_encoder.classes_ = ['baixo', 'medio', 'alto']
        mock_get_model.return_value = mock_model
        
        response = client.get("/predict?municipio=Kuito&ano_semana=2024-01")
        assert response.status_code == 200
        
            data = response.json()
        assert "municipio" in data
        assert "ano_semana" in data
        assert "classe_risco" in data
        assert "score_risco" in data
        assert "probabilidade_baixo" in data
        assert "probabilidade_medio" in data
        assert "probabilidade_alto" in data
        assert "modelo_versao" in data
        assert "created_at" in data
    
    @patch('src.api.endpoints.get_malaria_model')
    def test_predict_risk_model_not_trained(self, mock_get_model, client):
        """Testa predição com modelo não treinado."""
        # Mock do modelo não treinado
        mock_model = Mock()
        mock_model.model = None
        mock_get_model.return_value = mock_model
        
        response = client.get("/predict?municipio=Kuito&ano_semana=2024-01")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "Modelo não treinado" in data["detail"]
    
    @patch('src.api.endpoints.db_manager')
    def test_predict_risk_municipality_not_found(self, mock_db, client):
        """Testa predição para município não encontrado."""
        mock_db.get_series_semanais.return_value = []
        
        response = client.get("/predict?municipio=MunicipioInexistente&ano_semana=2024-01")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Município" in data["detail"]


class TestAPIIntegration:
    """Testes de integração para a API."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste para a API."""
        return TestClient(app)
    
    @patch('src.api.endpoints.db_manager')
    def test_full_prediction_flow(self, mock_db, client, sample_weekly_data, sample_predictions):
        """Testa fluxo completo de predição."""
        # Mock dos dados
        mock_db.get_series_semanais.return_value = sample_weekly_data
        mock_db.get_previsoes.return_value = sample_predictions
        
        # 1. Verificar saúde da API
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Obter municípios
        municipios_response = client.get("/municipios")
        assert municipios_response.status_code == 200
        
        # 3. Obter previsões
        previsoes_response = client.get("/previsoes/semana/2024-01")
        assert previsoes_response.status_code == 200
        
        # 4. Obter métricas
        metrics_response = client.get("/metrics/latest")
        # Pode retornar 404 se não houver métricas, o que é aceitável
        assert metrics_response.status_code in [200, 404]
    
    def test_cors_headers(self, client):
        """Testa headers CORS."""
        response = client.options("/")
        # CORS é configurado no middleware, então deve retornar 200
        assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Testa tratamento de erros."""
        # Teste com endpoint inexistente
        response = client.get("/endpoint-inexistente")
        assert response.status_code == 404
        
        # Teste com parâmetros inválidos
        response = client.get("/predict")
        assert response.status_code == 422  # Validation error