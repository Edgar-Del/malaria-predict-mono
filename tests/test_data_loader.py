"""
Testes para o módulo de carregamento de dados.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os

from src.ingest.data_loader import DataLoader


class TestDataLoader:
    """Testes para a classe DataLoader."""
    
    def test_init(self):
        """Testa inicialização do DataLoader."""
        loader = DataLoader()
        assert loader.data_path == "data/raw"
        assert loader.required_columns == [
            'municipio', 'data_caso', 'casos', 'chuva_mm', 'temp_media_c'
        ]
    
    def test_validate_data_schema_valid(self, sample_data):
        """Testa validação de schema com dados válidos."""
        loader = DataLoader()
        assert loader.validate_data_schema(sample_data) == True
    
    def test_validate_data_schema_invalid(self):
        """Testa validação de schema com dados inválidos."""
        loader = DataLoader()
        invalid_data = pd.DataFrame({
            'municipio': ['Kuito'],
            'data_caso': ['2024-01-01']
            # Faltam colunas obrigatórias
        })
        assert loader.validate_data_schema(invalid_data) == False
    
    def test_validate_data_quality(self, sample_data):
        """Testa validação de qualidade dos dados."""
        loader = DataLoader()
        issues = loader.validate_data_quality(sample_data)
        
        # Verificar se retorna dicionário com as chaves esperadas
        expected_keys = ['null_values', 'duplicates', 'outliers', 'invalid_dates', 'negative_values']
        assert all(key in issues for key in expected_keys)
    
    def test_clean_data(self, sample_data):
        """Testa limpeza de dados."""
        loader = DataLoader()
        
        # Adicionar alguns problemas aos dados
        dirty_data = sample_data.copy()
        dirty_data.loc[0, 'casos'] = -5  # Valor negativo
        dirty_data.loc[1, 'chuva_mm'] = np.nan  # Valor nulo
        dirty_data.loc[2, 'data_caso'] = 'invalid_date'  # Data inválida
        
        # Adicionar duplicata
        dirty_data = pd.concat([dirty_data, dirty_data.iloc[[0]]], ignore_index=True)
        
        cleaned_data = loader.clean_data(dirty_data)
        
        # Verificar se problemas foram corrigidos
        assert (cleaned_data['casos'] >= 0).all()  # Sem valores negativos
        assert cleaned_data['data_caso'].dtype == 'datetime64[ns]'  # Datas convertidas
        assert len(cleaned_data) < len(dirty_data)  # Duplicatas removidas
    
    def test_convert_to_epidemiological_week(self):
        """Testa conversão para semana epidemiológica."""
        loader = DataLoader()
        
        # Teste com data conhecida
        test_date = datetime(2024, 1, 15)  # Segunda-feira da 3ª semana de 2024
        week = loader.convert_to_epidemiological_week(test_date)
        assert week == "2024-03"
    
    def test_aggregate_by_week(self, sample_data):
        """Testa agregação por semana."""
        loader = DataLoader()
        
        # Converter data_caso para datetime
        sample_data['data_caso'] = pd.to_datetime(sample_data['data_caso'])
        
        weekly_data = loader.aggregate_by_week(sample_data)
        
        # Verificar se agregação foi feita corretamente
        assert 'ano_semana' in weekly_data.columns
        assert len(weekly_data) <= len(sample_data)  # Deve ter menos registros
        
        # Verificar se dados foram agregados por município e semana
        grouped = weekly_data.groupby(['municipio', 'ano_semana']).size()
        assert (grouped == 1).all()  # Cada combinação deve aparecer apenas uma vez
    
    def test_load_and_process_data(self, sample_data, data_loader):
        """Testa carregamento e processamento completo."""
        # Salvar dados de exemplo em arquivo temporário
        temp_file = os.path.join(data_loader.data_path, 'test_data.csv')
        sample_data.to_csv(temp_file, index=False)
        
        # Processar dados
        processed_data = data_loader.load_and_process_data('test_data.csv')
        
        # Verificar se processamento foi bem-sucedido
        assert len(processed_data) > 0
        assert 'ano_semana' in processed_data.columns
        assert processed_data['municipio'].nunique() == sample_data['municipio'].nunique()
    
    def test_create_sample_data(self, data_loader):
        """Testa criação de dados de exemplo."""
        output_file = os.path.join(data_loader.data_path, 'sample_test.csv')
        
        # Criar dados de exemplo
        from src.ingest.data_loader import create_sample_data
        create_sample_data(output_file)
        
        # Verificar se arquivo foi criado
        assert os.path.exists(output_file)
        
        # Carregar e verificar dados
        df = pd.read_csv(output_file)
        assert len(df) > 0
        assert all(col in df.columns for col in data_loader.required_columns)
        
        # Verificar se há dados para todos os municípios do Bié
        expected_municipios = [
            'Kuito', 'Camacupa', 'Catabola', 'Chinguar', 'Chitembo',
            'Cuemba', 'Cunhinga', 'Nharea', 'Andulo'
        ]
        assert all(municipio in df['municipio'].values for municipio in expected_municipios)


class TestDataLoaderIntegration:
    """Testes de integração para DataLoader."""
    
    def test_full_pipeline(self, data_loader):
        """Testa pipeline completo de carregamento e processamento."""
        # Criar dados de exemplo
        from src.ingest.data_loader import create_sample_data
        sample_file = os.path.join(data_loader.data_path, 'integration_test.csv')
        create_sample_data(sample_file)
        
        # Processar dados
        processed_data = data_loader.load_and_process_data('integration_test.csv')
        
        # Verificações finais
        assert len(processed_data) > 0
        assert processed_data['ano_semana'].str.match(r'\d{4}-\d{2}').all()
        assert processed_data['casos'].min() >= 0
        assert processed_data['chuva_mm'].min() >= 0
        
        # Verificar se não há valores nulos nas colunas principais
        main_columns = ['municipio', 'ano_semana', 'casos']
        assert not processed_data[main_columns].isnull().any().any()