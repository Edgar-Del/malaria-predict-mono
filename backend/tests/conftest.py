"""
Configuração de fixtures para testes.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import datetime, timedelta

from src.ingest.data_loader import DataLoader


@pytest.fixture
def sample_data():
    """Dados de exemplo para testes."""
    return pd.DataFrame({
        'municipio': ['Kuito', 'Camacupa', 'Andulo', 'Kuito', 'Camacupa'],
        'data_caso': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-08', '2024-01-09'],
        'casos': [10, 5, 8, 12, 7],
        'chuva_mm': [50.0, 30.0, 40.0, 60.0, 35.0],
        'temp_media_c': [25.0, 24.0, 23.0, 26.0, 24.5],
        'temp_min_c': [20.0, 19.0, 18.0, 21.0, 19.5],
        'temp_max_c': [30.0, 29.0, 28.0, 31.0, 29.5],
        'umidade_relativa': [70.0, 65.0, 75.0, 80.0, 68.0]
    })


@pytest.fixture
def data_loader():
    """Instância do DataLoader com diretório temporário."""
    temp_dir = tempfile.mkdtemp()
    loader = DataLoader(data_path=temp_dir)
    
    yield loader
    
    # Limpeza após o teste
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_database_manager():
    """Mock do DatabaseManager para testes."""
    class MockDatabaseManager:
        def __init__(self):
            self.municipios = [
                {'id': 1, 'nome': 'Kuito', 'latitude': -12.3833, 'longitude': 17.0000},
                {'id': 2, 'nome': 'Camacupa', 'latitude': -12.0167, 'longitude': 17.4833},
                {'id': 3, 'nome': 'Andulo', 'latitude': -11.4833, 'longitude': 16.4167}
            ]
            
            self.series_semanais = pd.DataFrame({
                'municipio_nome': ['Kuito', 'Camacupa', 'Andulo'],
                'ano_semana': ['2024-01', '2024-01', '2024-01'],
                'casos': [10, 5, 8],
                'chuva_mm': [50.0, 30.0, 40.0],
                'temp_media_c': [25.0, 24.0, 23.0]
            })
            
            self.previsoes = pd.DataFrame({
                'municipio_nome': ['Kuito', 'Camacupa', 'Andulo'],
                'ano_semana_prevista': ['2024-02', '2024-02', '2024-02'],
                'classe_risco': ['alto', 'medio', 'baixo'],
                'score_risco': [0.85, 0.65, 0.35],
                'probabilidade_baixo': [0.05, 0.20, 0.60],
                'probabilidade_medio': [0.10, 0.65, 0.35],
                'probabilidade_alto': [0.85, 0.15, 0.05],
                'modelo_versao': ['v1.0.0', 'v1.0.0', 'v1.0.0'],
                'modelo_tipo': ['RandomForest', 'RandomForest', 'RandomForest'],
                'created_at': [datetime.now(), datetime.now(), datetime.now()]
            })
        
        def test_connection(self):
            return True
        
        def get_municipios(self):
            return self.municipios
        
        def get_series_semanais(self, municipio_id=None, limit=None):
            if municipio_id:
                return self.series_semanais[self.series_semanais['municipio_nome'] == 'Kuito']
            return self.series_semanais
        
        def get_previsoes(self, ano_semana=None, municipio_id=None):
            if ano_semana:
                return self.previsoes[self.previsoes['ano_semana_prevista'] == ano_semana]
            return self.previsoes
        
        def insert_metricas(self, metricas):
            return True
        
        def insert_previsoes(self, df):
            return True
    
    return MockDatabaseManager()


@pytest.fixture
def sample_features_data():
    """Dados de features para testes."""
    return pd.DataFrame({
        'municipio': ['Kuito', 'Camacupa', 'Andulo'],
        'ano_semana': ['2024-01', '2024-02', '2024-03'],
        'casos': [10, 15, 8],
        'chuva_mm': [50.0, 60.0, 40.0],
        'temp_media_c': [25.0, 26.0, 24.0],
        'casos_lag1': [8, 10, 15],
        'casos_lag2': [5, 8, 10],
        'casos_media_2s': [9.0, 12.5, 11.5],
        'casos_media_4s': [8.5, 10.0, 12.0],
        'classe_risco': ['baixo', 'medio', 'baixo']
    })


@pytest.fixture
def mock_model():
    """Mock de modelo para testes."""
    class MockModel:
        def __init__(self):
            self.feature_importances_ = np.array([0.3, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05, 0.05])
        
        def predict(self, X):
            return np.array(['alto', 'medio', 'baixo'])
        
        def predict_proba(self, X):
            return np.array([
                [0.1, 0.2, 0.7],  # alto
                [0.2, 0.6, 0.2],  # medio
                [0.6, 0.3, 0.1]   # baixo
            ])
    
    return MockModel()


@pytest.fixture
def mock_label_encoder():
    """Mock do LabelEncoder para testes."""
    class MockLabelEncoder:
        def __init__(self):
            self.classes_ = np.array(['baixo', 'medio', 'alto'])
        
        def fit_transform(self, y):
            return np.array([0, 1, 2])  # baixo, medio, alto
        
        def inverse_transform(self, y):
            return self.classes_[y]
    
    return MockLabelEncoder()