"""
Configuração de testes para pytest.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os

from src.ingest.data_loader import DataLoader
from src.features.feature_engineering import FeatureEngineer
from src.model.malaria_model import MalariaModel
from src.ingest.database_manager import DatabaseManager


@pytest.fixture
def sample_data():
    """Dados de exemplo para testes."""
    data = []
    municipios = ['Kuito', 'Camacupa', 'Andulo']
    
    for municipio in municipios:
        for i in range(52):  # 52 semanas
            data.append({
                'municipio': municipio,
                'data_caso': (datetime.now() - timedelta(weeks=52-i)).strftime('%Y-%m-%d'),
                'casos': max(0, int(np.random.normal(50, 20))),
                'chuva_mm': max(0, np.random.normal(100, 30)),
                'temp_media_c': np.random.normal(23, 3),
                'temp_min_c': np.random.normal(20, 2),
                'temp_max_c': np.random.normal(26, 2),
                'umidade_relativa': 60 + np.random.uniform(-20, 20)
            })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_weekly_data():
    """Dados semanais de exemplo para testes."""
    data = []
    municipios = ['Kuito', 'Camacupa', 'Andulo']
    
    for municipio in municipios:
        for i in range(52):
            year = 2023 + (i // 52)
            week = (i % 52) + 1
            data.append({
                'municipio': municipio,
                'ano_semana': f"{year}-{week:02d}",
                'casos': max(0, int(np.random.normal(50, 20))),
                'chuva_mm': max(0, np.random.normal(100, 30)),
                'temp_media_c': np.random.normal(23, 3)
            })
    
    return pd.DataFrame(data)


@pytest.fixture
def data_loader():
    """Instância do DataLoader para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        loader = DataLoader(data_path=temp_dir)
        yield loader


@pytest.fixture
def feature_engineer():
    """Instância do FeatureEngineer para testes."""
    return FeatureEngineer()


@pytest.fixture
def malaria_model():
    """Instância do MalariaModel para testes."""
    return MalariaModel(model_type='random_forest', random_state=42)


@pytest.fixture
def temp_model_path():
    """Caminho temporário para salvar modelo."""
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Limpar arquivo temporário
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_database_url():
    """URL de banco de dados mock para testes."""
    return "sqlite:///:memory:"


@pytest.fixture
def sample_predictions():
    """Previsões de exemplo para testes."""
    return [
        {
            'municipio': 'Kuito',
            'municipio_id': 1,
            'ano_semana': '2024-01',
            'classe_risco': 'alto',
            'score_risco': 0.85,
            'probabilidade_baixo': 0.1,
            'probabilidade_medio': 0.2,
            'probabilidade_alto': 0.7,
            'modelo_versao': 'v1.0.0',
            'created_at': datetime.now().isoformat()
        },
        {
            'municipio': 'Camacupa',
            'municipio_id': 2,
            'ano_semana': '2024-01',
            'classe_risco': 'medio',
            'score_risco': 0.65,
            'probabilidade_baixo': 0.2,
            'probabilidade_medio': 0.5,
            'probabilidade_alto': 0.3,
            'modelo_versao': 'v1.0.0',
            'created_at': datetime.now().isoformat()
        }
    ]


@pytest.fixture
def sample_municipalities():
    """Municípios de exemplo para testes."""
    return [
        {
            'id': 1,
            'nome': 'Kuito',
            'cod_ibge_local': 'BIE001',
            'latitude': -12.3833,
            'longitude': 17.0000,
            'populacao': 185000,
            'area_km2': 4814.0
        },
        {
            'id': 2,
            'nome': 'Camacupa',
            'cod_ibge_local': 'BIE002',
            'latitude': -12.0167,
            'longitude': 17.4833,
            'populacao': 45000,
            'area_km2': 7420.0
        }
    ]


@pytest.fixture
def sample_metrics():
    """Métricas de exemplo para testes."""
    return {
        'modelo_versao': 'v1.0.0',
        'modelo_tipo': 'RandomForest',
        'data_treinamento': datetime.now(),
        'accuracy': 0.8234,
        'precision_macro': 0.8156,
        'recall_macro': 0.8201,
        'f1_macro': 0.8178,
        'precision_baixo': 0.8500,
        'recall_baixo': 0.8200,
        'f1_baixo': 0.8348,
        'precision_medio': 0.7800,
        'recall_medio': 0.8100,
        'f1_medio': 0.7949,
        'precision_alto': 0.8200,
        'recall_alto': 0.8300,
        'f1_alto': 0.8250
    }