"""
Testes para o módulo de engenharia de features.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.features.feature_engineering import FeatureEngineer


class TestFeatureEngineer:
    """Testes para a classe FeatureEngineer."""
    
    def test_init(self):
        """Testa inicialização do FeatureEngineer."""
        engineer = FeatureEngineer()
        
        assert engineer.feature_columns is not None
        assert engineer.target_column == 'classe_risco'
        assert len(engineer.feature_columns) > 0
    
    def test_create_lag_features(self, sample_features_data):
        """Testa criação de features de lag."""
        engineer = FeatureEngineer()
        
        # Criar features de lag
        df_with_lags = engineer.create_lag_features(
            sample_features_data, 'casos', [1, 2]
        )
        
        # Verificar se colunas de lag foram criadas
        assert 'casos_lag1' in df_with_lags.columns
        assert 'casos_lag2' in df_with_lags.columns
        
        # Verificar se valores estão corretos (shifted)
        assert df_with_lags['casos_lag1'].iloc[1] == sample_features_data['casos'].iloc[0]
        assert df_with_lags['casos_lag2'].iloc[2] == sample_features_data['casos'].iloc[0]
    
    def test_create_rolling_features(self, sample_features_data):
        """Testa criação de features de média móvel."""
        engineer = FeatureEngineer()
        
        # Criar features de média móvel
        df_with_rolling = engineer.create_rolling_features(
            sample_features_data, 'casos', [2, 4]
        )
        
        # Verificar se colunas de média móvel foram criadas
        assert 'casos_media_2s' in df_with_rolling.columns
        assert 'casos_media_4s' in df_with_rolling.columns
        
        # Verificar se valores são numéricos
        assert pd.api.types.is_numeric_dtype(df_with_rolling['casos_media_2s'])
        assert pd.api.types.is_numeric_dtype(df_with_rolling['casos_media_4s'])
    
    def test_create_seasonal_features(self, sample_features_data):
        """Testa criação de features sazonais."""
        engineer = FeatureEngineer()
        
        # Criar features sazonais
        df_seasonal = engineer.create_seasonal_features(sample_features_data)
        
        # Verificar se colunas sazonais foram criadas
        assert 'semana_ano' in df_seasonal.columns
        assert 'semana_sin' in df_seasonal.columns
        assert 'semana_cos' in df_seasonal.columns
        assert 'periodo_chuva' in df_seasonal.columns
        assert 'periodo_seco' in df_seasonal.columns
        
        # Verificar se valores estão no range correto
        assert df_seasonal['semana_ano'].min() >= 1
        assert df_seasonal['semana_ano'].max() <= 53
        assert df_seasonal['semana_sin'].min() >= -1
        assert df_seasonal['semana_sin'].max() <= 1
        assert df_seasonal['semana_cos'].min() >= -1
        assert df_seasonal['semana_cos'].max() <= 1
    
    def test_create_climate_features(self, sample_features_data):
        """Testa criação de features climáticas."""
        engineer = FeatureEngineer()
        
        # Adicionar colunas necessárias
        df_climate = sample_features_data.copy()
        df_climate['temp_max_c'] = df_climate['temp_media_c'] + 5
        df_climate['temp_min_c'] = df_climate['temp_media_c'] - 5
        df_climate['umidade_relativa'] = 70.0
        
        # Criar features climáticas
        df_with_climate = engineer.create_climate_features(df_climate)
        
        # Verificar se colunas climáticas foram criadas
        assert 'amplitude_termica' in df_with_climate.columns
        assert 'indice_calor' in df_with_climate.columns
        assert 'chuva_acumulada_4s' in df_with_climate.columns
        assert 'temp_media_4s' in df_with_climate.columns
        
        # Verificar se amplitude térmica está correta
        expected_amplitude = df_climate['temp_max_c'] - df_climate['temp_min_c']
        assert np.allclose(df_with_climate['amplitude_termica'], expected_amplitude)
    
    def test_create_epidemiological_features(self, sample_features_data):
        """Testa criação de features epidemiológicas."""
        engineer = FeatureEngineer()
        
        # Criar features epidemiológicas
        df_epi = engineer.create_epidemiological_features(sample_features_data)
        
        # Verificar se colunas epidemiológicas foram criadas
        assert 'taxa_crescimento_casos' in df_epi.columns
        assert 'aceleracao_casos' in df_epi.columns
        assert 'casos_percentil' in df_epi.columns
        assert 'risco_percentil' in df_epi.columns
        
        # Verificar se percentis estão no range correto
        assert df_epi['casos_percentil'].min() >= 0
        assert df_epi['casos_percentil'].max() <= 1
    
    def test_create_target_variable_percentil(self, sample_features_data):
        """Testa criação de variável target usando método percentil."""
        engineer = FeatureEngineer()
        
        # Criar variável target
        df_target = engineer.create_target_variable(sample_features_data, method='percentil')
        
        # Verificar se coluna target foi criada
        assert 'classe_risco' in df_target.columns
        
        # Verificar se classes estão corretas
        expected_classes = ['baixo', 'medio', 'alto']
        assert df_target['classe_risco'].isin(expected_classes).all()
    
    def test_create_target_variable_threshold(self, sample_features_data):
        """Testa criação de variável target usando método threshold."""
        engineer = FeatureEngineer()
        
        # Criar variável target
        df_target = engineer.create_target_variable(sample_features_data, method='threshold')
        
        # Verificar se coluna target foi criada
        assert 'classe_risco' in df_target.columns
        
        # Verificar se classes estão corretas
        expected_classes = ['baixo', 'medio', 'alto']
        assert df_target['classe_risco'].isin(expected_classes).all()
    
    def test_engineer_features(self, sample_features_data):
        """Testa pipeline completo de engenharia de features."""
        engineer = FeatureEngineer()
        
        # Aplicar engenharia de features
        df_engineered = engineer.engineer_features(sample_features_data)
        
        # Verificar se features foram criadas
        assert len(df_engineered.columns) > len(sample_features_data.columns)
        
        # Verificar se colunas esperadas estão presentes
        expected_features = ['casos_lag1', 'casos_lag2', 'casos_media_2s', 'classe_risco']
        for feature in expected_features:
            assert feature in df_engineered.columns
        
        # Verificar se não há valores nulos nas colunas principais
        main_columns = ['municipio', 'ano_semana', 'casos', 'classe_risco']
        assert not df_engineered[main_columns].isnull().any().any()
    
    def test_prepare_training_data(self, sample_features_data):
        """Testa preparação de dados para treinamento."""
        engineer = FeatureEngineer()
        
        # Aplicar engenharia de features primeiro
        df_engineered = engineer.engineer_features(sample_features_data)
        
        # Preparar dados para treinamento
        X, y = engineer.prepare_training_data(df_engineered)
        
        # Verificar se X e y têm o mesmo número de amostras
        assert len(X) == len(y)
        
        # Verificar se X contém apenas features numéricas
        assert X.select_dtypes(include=[np.number]).shape[1] == X.shape[1]
        
        # Verificar se y contém apenas valores numéricos
        assert pd.api.types.is_numeric_dtype(y)
    
    def test_get_feature_importance(self, mock_model):
        """Testa obtenção de importância das features."""
        engineer = FeatureEngineer()
        feature_names = ['feature1', 'feature2', 'feature3', 'feature4', 
                        'feature5', 'feature6', 'feature7', 'feature8']
        
        importance = engineer.get_feature_importance(mock_model, feature_names)
        
        # Verificar se retorna dicionário
        assert isinstance(importance, dict)
        
        # Verificar se todas as features estão presentes
        assert len(importance) == len(feature_names)
        
        # Verificar se valores são numéricos
        assert all(isinstance(v, (int, float)) for v in importance.values())
        
        # Verificar se está ordenado por importância
        values = list(importance.values())
        assert values == sorted(values, reverse=True)
    
    def test_validate_features(self, sample_features_data):
        """Testa validação de features."""
        engineer = FeatureEngineer()
        
        # Aplicar engenharia de features
        df_engineered = engineer.engineer_features(sample_features_data)
        
        # Validar features
        issues = engineer.validate_features(df_engineered)
        
        # Verificar se retorna dicionário com chaves esperadas
        expected_keys = ['missing_values', 'infinite_values', 'constant_features', 'high_correlation']
        assert all(key in issues for key in expected_keys)
        
        # Verificar se todas as chaves contêm listas
        for key in expected_keys:
            assert isinstance(issues[key], list)


class TestFeatureEngineerIntegration:
    """Testes de integração para FeatureEngineer."""
    
    def test_full_pipeline_with_real_data(self, data_loader):
        """Testa pipeline completo com dados reais."""
        # Criar dados de exemplo
        from src.ingest.data_loader import create_sample_data
        sample_file = os.path.join(data_loader.data_path, 'integration_test.csv')
        create_sample_data(sample_file)
        
        # Carregar e processar dados
        df_processed = data_loader.load_and_process_data('integration_test.csv')
        
        # Aplicar engenharia de features
        engineer = FeatureEngineer()
        df_features = engineer.engineer_features(df_processed)
        
        # Verificar se pipeline foi bem-sucedido
        assert len(df_features) > 0
        assert 'classe_risco' in df_features.columns
        
        # Preparar dados para treinamento
        X, y = engineer.prepare_training_data(df_features)
        
        # Verificar se dados estão prontos para treinamento
        assert len(X) > 0
        assert len(y) > 0
        assert X.shape[1] > 0
        assert not X.isnull().any().any()
    
    def test_feature_consistency(self, sample_features_data):
        """Testa consistência das features criadas."""
        engineer = FeatureEngineer()
        
        # Aplicar engenharia de features múltiplas vezes
        df1 = engineer.engineer_features(sample_features_data)
        df2 = engineer.engineer_features(sample_features_data)
        
        # Verificar se resultados são consistentes
        assert df1.shape == df2.shape
        assert list(df1.columns) == list(df2.columns)
        
        # Verificar se valores numéricos são consistentes
        numeric_cols = df1.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert np.allclose(df1[col], df2[col], equal_nan=True)