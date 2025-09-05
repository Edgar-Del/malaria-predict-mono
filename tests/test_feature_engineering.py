"""
Testes para o módulo de engenharia de atributos.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.features.feature_engineering import FeatureEngineer


class TestFeatureEngineer:
    """Testes para a classe FeatureEngineer."""
    
    def test_init(self):
        """Testa inicialização do FeatureEngineer."""
        engineer = FeatureEngineer()
        assert engineer.feature_columns == []
        assert engineer.target_column == 'risco_futuro'
    
    def test_create_lag_features(self, sample_weekly_data):
        """Testa criação de features de lag."""
        engineer = FeatureEngineer()
        
        # Ordenar dados por município e tempo
        df = sample_weekly_data.sort_values(['municipio', 'ano_semana']).reset_index(drop=True)
        
        # Criar features de lag
        lag_columns = ['casos', 'chuva_mm']
        lag_periods = [1, 2]
        
        df_with_lags = engineer.create_lag_features(df, lag_columns, lag_periods)
        
        # Verificar se features foram criadas
        expected_lag_cols = ['casos_lag1', 'casos_lag2', 'chuva_mm_lag1', 'chuva_mm_lag2']
        for col in expected_lag_cols:
            assert col in df_with_lags.columns
            assert col in engineer.feature_columns
        
        # Verificar se lags estão corretos para o primeiro município
        first_municipality = df['municipio'].iloc[0]
        first_municipality_data = df_with_lags[df_with_lags['municipio'] == first_municipality].reset_index(drop=True)
        
        # Primeira linha deve ter NaN para lags
        assert pd.isna(first_municipality_data['casos_lag1'].iloc[0])
        assert pd.isna(first_municipality_data['casos_lag2'].iloc[0])
        
        # Segunda linha deve ter lag1 = primeira linha
        if len(first_municipality_data) > 1:
            assert first_municipality_data['casos_lag1'].iloc[1] == first_municipality_data['casos'].iloc[0]
    
    def test_create_rolling_features(self, sample_weekly_data):
        """Testa criação de features de janelas móveis."""
        engineer = FeatureEngineer()
        
        df = sample_weekly_data.sort_values(['municipio', 'ano_semana']).reset_index(drop=True)
        
        rolling_columns = ['casos', 'chuva_mm']
        rolling_windows = [2, 4]
        
        df_with_rolling = engineer.create_rolling_features(df, rolling_columns, rolling_windows)
        
        # Verificar se features foram criadas
        expected_rolling_cols = [
            'casos_media_2s', 'casos_std_2s', 'casos_max_2s',
            'casos_media_4s', 'casos_std_4s', 'casos_max_4s',
            'chuva_mm_media_2s', 'chuva_mm_std_2s', 'chuva_mm_max_2s',
            'chuva_mm_media_4s', 'chuva_mm_std_4s', 'chuva_mm_max_4s'
        ]
        
        for col in expected_rolling_cols:
            assert col in df_with_rolling.columns
            assert col in engineer.feature_columns
    
    def test_create_temporal_features(self, sample_weekly_data):
        """Testa criação de features temporais."""
        engineer = FeatureEngineer()
        
        df_with_temporal = engineer.create_temporal_features(sample_weekly_data)
        
        # Verificar se features temporais foram criadas
        temporal_cols = ['ano', 'semana', 'semana_sin', 'semana_cos', 'tendencia', 'estacao']
        for col in temporal_cols:
            assert col in df_with_temporal.columns
            assert col in engineer.feature_columns
        
        # Verificar se valores estão no range esperado
        assert df_with_temporal['ano'].min() >= 2020
        assert df_with_temporal['semana'].min() >= 1
        assert df_with_temporal['semana'].max() <= 53
        assert df_with_temporal['semana_sin'].min() >= -1
        assert df_with_temporal['semana_sin'].max() <= 1
        assert df_with_temporal['semana_cos'].min() >= -1
        assert df_with_temporal['semana_cos'].max() <= 1
    
    def test_create_interaction_features(self, sample_weekly_data):
        """Testa criação de features de interação."""
        engineer = FeatureEngineer()
        
        df_with_interaction = engineer.create_interaction_features(sample_weekly_data)
        
        # Verificar se features de interação foram criadas
        interaction_cols = ['chuva_temp_interaction', 'casos_chuva_interaction', 'chuva_temp_ratio']
        for col in interaction_cols:
            if col in df_with_interaction.columns:
                assert col in engineer.feature_columns
    
    def test_create_risk_label(self, sample_weekly_data):
        """Testa criação de rótulo de risco."""
        engineer = FeatureEngineer()
        
        df_with_labels = engineer.create_risk_label(sample_weekly_data)
        
        # Verificar se coluna de risco foi criada
        assert 'risco_futuro' in df_with_labels.columns
        assert 'casos_futuro' in df_with_labels.columns
        
        # Verificar se rótulos estão corretos
        risk_values = df_with_labels['risco_futuro'].unique()
        expected_risks = ['baixo', 'medio', 'alto']
        assert all(risk in expected_risks for risk in risk_values if pd.notna(risk))
    
    def test_create_all_features(self, sample_weekly_data):
        """Testa criação de todas as features."""
        engineer = FeatureEngineer()
        
        df_with_features = engineer.create_all_features(sample_weekly_data)
        
        # Verificar se features foram criadas
        assert len(engineer.feature_columns) > 0
        assert all(col in df_with_features.columns for col in engineer.feature_columns)
        
        # Verificar se dados não foram perdidos
        assert len(df_with_features) > 0
        
        # Verificar se target foi criado
        assert 'risco_futuro' in df_with_features.columns
    
    def test_prepare_training_data(self, sample_weekly_data):
        """Testa preparação de dados para treinamento."""
        engineer = FeatureEngineer()
        
        # Criar features
        df_with_features = engineer.create_all_features(sample_weekly_data)
        
        # Preparar dados de treinamento
        X, y = engineer.prepare_training_data(df_with_features)
        
        # Verificar se X e y têm o mesmo número de linhas
        assert len(X) == len(y)
        
        # Verificar se X contém apenas features numéricas
        assert X.select_dtypes(include=[np.number]).shape[1] == X.shape[1]
        
        # Verificar se não há valores nulos
        assert not X.isnull().any().any()
        assert not y.isnull().any()
    
    def test_impute_missing_values(self, sample_weekly_data):
        """Testa imputação de valores ausentes."""
        engineer = FeatureEngineer()
        
        # Criar features
        df_with_features = engineer.create_all_features(sample_weekly_data)
        
        # Adicionar valores nulos artificialmente
        df_with_nulls = df_with_features.copy()
        df_with_nulls.loc[0, 'casos_lag1'] = np.nan
        df_with_nulls.loc[1, 'chuva_mm_media_2s'] = np.nan
        
        # Imputar valores ausentes
        df_imputed = engineer.impute_missing_values(df_with_nulls)
        
        # Verificar se valores nulos foram imputados
        assert not df_imputed[engineer.feature_columns].isnull().any().any()
    
    def test_get_feature_columns(self, sample_weekly_data):
        """Testa obtenção de colunas de features."""
        engineer = FeatureEngineer()
        
        # Criar features
        engineer.create_all_features(sample_weekly_data)
        
        # Obter colunas de features
        feature_cols = engineer.get_feature_columns()
        
        # Verificar se retorna lista
        assert isinstance(feature_cols, list)
        assert len(feature_cols) > 0
        
        # Verificar se é uma cópia (não referência)
        assert feature_cols is not engineer.feature_columns


class TestFeatureEngineerIntegration:
    """Testes de integração para FeatureEngineer."""
    
    def test_full_feature_pipeline(self, sample_weekly_data):
        """Testa pipeline completo de criação de features."""
        engineer = FeatureEngineer()
        
        # Pipeline completo
        df_with_features = engineer.create_all_features(sample_weekly_data)
        X, y = engineer.prepare_training_data(df_with_features)
        
        # Verificações finais
        assert len(X) > 0
        assert len(y) > 0
        assert len(engineer.feature_columns) > 0
        
        # Verificar se todas as features são numéricas
        assert X.select_dtypes(include=[np.number]).shape[1] == X.shape[1]
        
        # Verificar se não há valores nulos
        assert not X.isnull().any().any()
        assert not y.isnull().any()
        
        # Verificar se target tem valores válidos
        valid_targets = ['baixo', 'medio', 'alto']
        assert all(target in valid_targets for target in y.unique() if pd.notna(target))