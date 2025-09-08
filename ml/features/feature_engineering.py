"""
Módulo para engenharia de atributos (features) para o modelo de previsão de malária.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Classe para engenharia de atributos."""
    
    def __init__(self):
        self.feature_columns = []
        self.target_column = 'risco_futuro'
    
    def create_lag_features(self, df: pd.DataFrame, 
                          columns: List[str], 
                          lags: List[int]) -> pd.DataFrame:
        """
        Cria features de lag (valores passados).
        
        Args:
            df: DataFrame com dados ordenados por município e tempo
            columns: Colunas para criar lags
            lags: Lista de lags a criar (ex: [1, 2, 3, 4])
            
        Returns:
            DataFrame com features de lag adicionadas
        """
        df_lagged = df.copy()
        
        for col in columns:
            if col in df.columns:
                for lag in lags:
                    lag_col = f"{col}_lag{lag}"
                    df_lagged[lag_col] = df_lagged.groupby('municipio')[col].shift(lag)
                    self.feature_columns.append(lag_col)
        
        logger.info(f"Features de lag criadas: {len(lags)} lags para {len(columns)} colunas")
        return df_lagged
    
    def create_rolling_features(self, df: pd.DataFrame, 
                              columns: List[str], 
                              windows: List[int]) -> pd.DataFrame:
        """
        Cria features de janelas móveis (médias, desvios, etc.).
        
        Args:
            df: DataFrame com dados ordenados por município e tempo
            columns: Colunas para criar janelas móveis
            windows: Lista de janelas (ex: [2, 4, 8])
            
        Returns:
            DataFrame com features de janelas móveis adicionadas
        """
        df_rolling = df.copy()
        
        for col in columns:
            if col in df.columns:
                for window in windows:
                    # Média móvel
                    mean_col = f"{col}_media_{window}s"
                    df_rolling[mean_col] = (
                        df_rolling.groupby('municipio')[col]
                        .rolling(window=window, min_periods=1)
                        .mean()
                        .reset_index(0, drop=True)
                    )
                    self.feature_columns.append(mean_col)
                    
                    # Desvio padrão móvel
                    std_col = f"{col}_std_{window}s"
                    df_rolling[std_col] = (
                        df_rolling.groupby('municipio')[col]
                        .rolling(window=window, min_periods=1)
                        .std()
                        .reset_index(0, drop=True)
                    )
                    self.feature_columns.append(std_col)
                    
                    # Máximo móvel
                    max_col = f"{col}_max_{window}s"
                    df_rolling[max_col] = (
                        df_rolling.groupby('municipio')[col]
                        .rolling(window=window, min_periods=1)
                        .max()
                        .reset_index(0, drop=True)
                    )
                    self.feature_columns.append(max_col)
        
        logger.info(f"Features de janelas móveis criadas: {len(windows)} janelas para {len(columns)} colunas")
        return df_rolling
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features temporais (sazonalidade, tendências).
        
        Args:
            df: DataFrame com colunas 'ano' e 'semana'
            
        Returns:
            DataFrame com features temporais adicionadas
        """
        df_temporal = df.copy()
        
        # Verificar se as colunas ano e semana existem
        if 'ano' not in df_temporal.columns or 'semana' not in df_temporal.columns:
            logger.warning("Colunas 'ano' e 'semana' não encontradas. Pulando features temporais.")
            return df_temporal
        
        # Features cíclicas para sazonalidade
        df_temporal['semana_sin'] = np.sin(2 * np.pi * df_temporal['semana'] / 52)
        df_temporal['semana_cos'] = np.cos(2 * np.pi * df_temporal['semana'] / 52)
        
        # Tendência temporal (número de semanas desde início)
        df_temporal['tendencia'] = (
            (df_temporal['ano'] - df_temporal['ano'].min()) * 52 + 
            (df_temporal['semana'] - df_temporal['semana'].min())
        )
        
        # Estação do ano (aproximada)
        df_temporal['estacao'] = ((df_temporal['semana'] - 1) // 13) + 1
        
        # Features cíclicas para mês
        if 'mes' in df_temporal.columns:
            df_temporal['mes_sin'] = np.sin(2 * np.pi * df_temporal['mes'] / 12)
            df_temporal['mes_cos'] = np.cos(2 * np.pi * df_temporal['mes'] / 12)
            self.feature_columns.extend(['mes_sin', 'mes_cos'])
        
        self.feature_columns.extend([
            'semana_sin', 'semana_cos', 'tendencia', 'estacao'
        ])
        
        logger.info("Features temporais criadas")
        return df_temporal
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de interação entre variáveis.
        
        Args:
            df: DataFrame com features básicas
            
        Returns:
            DataFrame com features de interação adicionadas
        """
        df_interaction = df.copy()
        
        # Interação entre chuva e temperatura
        if 'chuva_mm' in df.columns and 'temp_media_c' in df.columns:
            df_interaction['chuva_temp_interaction'] = (
                df_interaction['chuva_mm'] * df_interaction['temp_media_c']
            )
            self.feature_columns.append('chuva_temp_interaction')
        
        # Interação entre casos e chuva (lag)
        if 'casos' in df.columns and 'chuva_mm_lag1' in df.columns:
            df_interaction['casos_chuva_interaction'] = (
                df_interaction['casos'] * df_interaction['chuva_mm_lag1']
            )
            self.feature_columns.append('casos_chuva_interaction')
        
        # Razão chuva/temperatura
        if 'chuva_mm' in df.columns and 'temp_media_c' in df.columns:
            df_interaction['chuva_temp_ratio'] = (
                df_interaction['chuva_mm'] / (df_interaction['temp_media_c'] + 1e-8)
            )
            self.feature_columns.append('chuva_temp_ratio')
        
        logger.info("Features de interação criadas")
        return df_interaction
    
    def create_risk_label(self, df: pd.DataFrame, 
                         target_column: str = 'casos',
                         method: str = 'quantile') -> pd.DataFrame:
        """
        Cria rótulo de risco baseado em casos futuros.
        
        Args:
            df: DataFrame com dados ordenados por município e tempo
            target_column: Coluna para calcular risco
            method: Método para calcular limiares ('quantile' ou 'absolute')
            
        Returns:
            DataFrame com coluna de risco adicionada
        """
        df_labeled = df.copy()
        
        # Criar coluna de casos futuros (próxima semana)
        df_labeled['casos_futuro'] = (
            df_labeled.groupby('municipio')[target_column].shift(-1)
        )
        
        # Calcular limiares de risco por município
        risk_labels = []
        
        for municipio in df_labeled['municipio'].unique():
            municipio_data = df_labeled[df_labeled['municipio'] == municipio].copy()
            
            if method == 'quantile':
                # Usar quantis para definir limiares
                q33 = municipio_data['casos_futuro'].quantile(0.33)
                q66 = municipio_data['casos_futuro'].quantile(0.66)
            else:
                # Usar limiares absolutos (ajustar conforme necessário)
                q33 = 20  # Baixo risco
                q66 = 50  # Médio risco
            
            # Aplicar rótulos
            municipio_data['risco_futuro'] = pd.cut(
                municipio_data['casos_futuro'],
                bins=[-np.inf, q33, q66, np.inf],
                labels=['baixo', 'medio', 'alto']
            )
            
            risk_labels.append(municipio_data)
        
        df_labeled = pd.concat(risk_labels, ignore_index=True)
        
        # Remover linhas sem rótulo (última semana de cada município)
        df_labeled = df_labeled.dropna(subset=['risco_futuro'])
        
        logger.info(f"Rótulos de risco criados: {len(df_labeled)} registros")
        return df_labeled
    
    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria todas as features para o modelo.
        
        Args:
            df: DataFrame com dados básicos (municipio, ano_semana, casos, chuva_mm, temp_media_c)
            
        Returns:
            DataFrame com todas as features criadas
        """
        logger.info("Iniciando criação de features")
        
        # Garantir que os dados estão ordenados
        df = df.sort_values(['municipio', 'ano_semana']).reset_index(drop=True)
        
        # Features de lag
        lag_columns = ['casos', 'chuva_mm', 'temp_media_c']
        lag_periods = [1, 2, 3, 4]
        df = self.create_lag_features(df, lag_columns, lag_periods)
        
        # Features de janelas móveis
        rolling_columns = ['casos', 'chuva_mm', 'temp_media_c']
        rolling_windows = [2, 4, 8]
        df = self.create_rolling_features(df, rolling_columns, rolling_windows)
        
        # Features temporais
        df = self.create_temporal_features(df)
        
        # Features de interação
        df = self.create_interaction_features(df)
        
        # Rótulo de risco
        df = self.create_risk_label(df)
        
        # Remover colunas auxiliares
        df = df.drop(['casos_futuro'], axis=1, errors='ignore')
        
        logger.info(f"Features criadas: {len(self.feature_columns)} colunas")
        logger.info(f"Features: {self.feature_columns}")
        
        return df
    
    def get_feature_columns(self) -> List[str]:
        """Retorna lista de colunas de features."""
        return self.feature_columns.copy()
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara dados para treinamento do modelo.
        
        Args:
            df: DataFrame com features criadas
            
        Returns:
            Tuple com (X, y) para treinamento
        """
        # Selecionar apenas features numéricas
        numeric_features = df[self.feature_columns].select_dtypes(include=[np.number])
        
        # Remover linhas com valores nulos
        clean_data = numeric_features.dropna()
        
        # Separar features e target
        X = clean_data
        y = df.loc[clean_data.index, self.target_column]
        
        logger.info(f"Dados de treinamento preparados: {len(X)} amostras, {len(X.columns)} features")
        
        return X, y
    
    def impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Imputa valores ausentes nas features.
        
        Args:
            df: DataFrame com features
            
        Returns:
            DataFrame com valores imputados
        """
        df_imputed = df.copy()
        
        # Imputar por média móvel por município
        for col in self.feature_columns:
            if col in df_imputed.columns:
                df_imputed[col] = (
                    df_imputed.groupby('municipio')[col]
                    .transform(lambda x: x.fillna(x.rolling(window=4, min_periods=1).mean()))
                )
        
        # Se ainda houver valores nulos, imputar com média global
        for col in self.feature_columns:
            if col in df_imputed.columns:
                df_imputed[col] = df_imputed[col].fillna(df_imputed[col].mean())
        
        logger.info("Valores ausentes imputados")
        return df_imputed


def create_sample_features_data() -> pd.DataFrame:
    """
    Cria dados de exemplo com features para desenvolvimento.
    
    Returns:
        DataFrame com dados de exemplo
    """
    # Criar dados de exemplo
    municipios = ['Kuito', 'Camacupa', 'Andulo']
    data = []
    
    for municipio in municipios:
        for year in [2023, 2024]:
            for week in range(1, 53):
                # Dados simulados
                casos = max(0, int(np.random.normal(50, 20)))
                chuva = max(0, np.random.normal(100, 30))
                temp = np.random.normal(23, 3)
                
                data.append({
                    'municipio': municipio,
                    'ano_semana': f"{year}-{week:02d}",
                    'casos': casos,
                    'chuva_mm': round(chuva, 2),
                    'temp_media_c': round(temp, 2)
                })
    
    df = pd.DataFrame(data)
    
    # Criar features
    engineer = FeatureEngineer()
    df_with_features = engineer.create_all_features(df)
    
    return df_with_features


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar dados de exemplo
    df = create_sample_features_data()
    print(f"Dados com features: {len(df)} registros")
    print(f"Features criadas: {len(df.columns)} colunas")
    print(df.head())