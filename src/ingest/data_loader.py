"""
Módulo para carregamento e validação de dados de casos de malária e clima.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    """Classe para carregamento e validação de dados."""
    
    def __init__(self, data_path: str = "data/raw"):
        self.data_path = Path(data_path)
        self.required_columns = [
            'municipio', 'data_caso', 'casos', 'chuva_mm', 'temp_media_c'
        ]
        
    def load_cases_data(self, filename: str) -> pd.DataFrame:
        """
        Carrega dados de casos de malária de um arquivo CSV.
        
        Args:
            filename: Nome do arquivo CSV
            
        Returns:
            DataFrame com os dados carregados
        """
        file_path = self.data_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Dados carregados: {len(df)} registros de {file_path}")
            return df
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
            raise
    
    def validate_data_schema(self, df: pd.DataFrame) -> bool:
        """
        Valida se o DataFrame possui o schema esperado.
        
        Args:
            df: DataFrame para validar
            
        Returns:
            True se válido, False caso contrário
        """
        missing_columns = set(self.required_columns) - set(df.columns)
        
        if missing_columns:
            logger.error(f"Colunas obrigatórias ausentes: {missing_columns}")
            return False
            
        logger.info("Schema validado com sucesso")
        return True
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, List]:
        """
        Valida a qualidade dos dados e retorna problemas encontrados.
        
        Args:
            df: DataFrame para validar
            
        Returns:
            Dicionário com problemas encontrados por tipo
        """
        issues = {
            'null_values': [],
            'duplicates': [],
            'outliers': [],
            'invalid_dates': [],
            'negative_values': []
        }
        
        # Verificar valores nulos
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                issues['null_values'].append(f"{col}: {count} valores nulos")
        
        # Verificar duplicatas
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues['duplicates'].append(f"{duplicates} registros duplicados")
        
        # Verificar datas inválidas
        if 'data_caso' in df.columns:
            try:
                pd.to_datetime(df['data_caso'], errors='coerce')
                invalid_dates = pd.to_datetime(df['data_caso'], errors='coerce').isnull().sum()
                if invalid_dates > 0:
                    issues['invalid_dates'].append(f"{invalid_dates} datas inválidas")
            except:
                issues['invalid_dates'].append("Erro ao processar coluna de datas")
        
        # Verificar valores negativos onde não deveriam existir
        numeric_columns = ['casos', 'chuva_mm']
        for col in numeric_columns:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    issues['negative_values'].append(f"{col}: {negative_count} valores negativos")
        
        # Verificar outliers grosseiros
        if 'casos' in df.columns:
            q99 = df['casos'].quantile(0.99)
            outliers = (df['casos'] > q99 * 3).sum()
            if outliers > 0:
                issues['outliers'].append(f"casos: {outliers} outliers extremos")
        
        if 'temp_media_c' in df.columns:
            # Temperaturas muito altas ou baixas para Angola
            extreme_temp = ((df['temp_media_c'] < 10) | (df['temp_media_c'] > 40)).sum()
            if extreme_temp > 0:
                issues['outliers'].append(f"temp_media_c: {extreme_temp} temperaturas extremas")
        
        return issues
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados aplicando correções básicas.
        
        Args:
            df: DataFrame para limpar
            
        Returns:
            DataFrame limpo
        """
        df_clean = df.copy()
        
        # Converter data_caso para datetime
        if 'data_caso' in df_clean.columns:
            df_clean['data_caso'] = pd.to_datetime(df_clean['data_caso'], errors='coerce')
        
        # Remover registros com datas inválidas
        df_clean = df_clean.dropna(subset=['data_caso'])
        
        # Remover duplicatas
        df_clean = df_clean.drop_duplicates()
        
        # Corrigir valores negativos
        numeric_columns = ['casos', 'chuva_mm']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(lower=0)
        
        # Imputar valores nulos com média móvel por município
        for col in ['chuva_mm', 'temp_media_c']:
            if col in df_clean.columns:
                df_clean[col] = df_clean.groupby('municipio')[col].transform(
                    lambda x: x.fillna(x.rolling(window=4, min_periods=1).mean())
                )
        
        logger.info(f"Dados limpos: {len(df_clean)} registros válidos")
        return df_clean
    
    def convert_to_epidemiological_week(self, date: datetime) -> str:
        """
        Converte uma data para formato de semana epidemiológica (YYYY-WW).
        
        Args:
            date: Data para converter
            
        Returns:
            String no formato YYYY-WW
        """
        year = date.year
        week = date.isocalendar()[1]
        return f"{year}-{week:02d}"
    
    def aggregate_by_week(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados por município e semana epidemiológica.
        
        Args:
            df: DataFrame com dados diários
            
        Returns:
            DataFrame agregado por semana
        """
        if 'data_caso' not in df.columns:
            raise ValueError("Coluna 'data_caso' não encontrada")
        
        # Converter para semana epidemiológica
        df['ano_semana'] = df['data_caso'].apply(self.convert_to_epidemiological_week)
        
        # Agregar por município e semana
        agg_dict = {
            'casos': 'sum',
            'chuva_mm': 'mean',
            'temp_media_c': 'mean'
        }
        
        # Adicionar colunas opcionais se existirem
        optional_cols = ['temp_min_c', 'temp_max_c', 'umidade_relativa']
        for col in optional_cols:
            if col in df.columns:
                agg_dict[col] = 'mean'
        
        df_weekly = df.groupby(['municipio', 'ano_semana']).agg(agg_dict).reset_index()
        
        # Ordenar por município e semana
        df_weekly = df_weekly.sort_values(['municipio', 'ano_semana'])
        
        logger.info(f"Dados agregados: {len(df_weekly)} registros semanais")
        return df_weekly
    
    def load_and_process_data(self, filename: str) -> pd.DataFrame:
        """
        Carrega, valida e processa dados de um arquivo CSV.
        
        Args:
            filename: Nome do arquivo CSV
            
        Returns:
            DataFrame processado e pronto para uso
        """
        # Carregar dados
        df = self.load_cases_data(filename)
        
        # Validar schema
        if not self.validate_data_schema(df):
            raise ValueError("Schema de dados inválido")
        
        # Validar qualidade
        issues = self.validate_data_quality(df)
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        if total_issues > 0:
            logger.warning(f"Problemas de qualidade encontrados: {total_issues}")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    logger.warning(f"{issue_type}: {issue_list}")
        
        # Limpar dados
        df_clean = self.clean_data(df)
        
        # Agregar por semana
        df_weekly = self.aggregate_by_week(df_clean)
        
        return df_weekly


def create_sample_data(output_path: str = "data/raw/sample_data.csv") -> None:
    """
    Cria dados de exemplo para desenvolvimento e testes.
    
    Args:
        output_path: Caminho para salvar o arquivo de exemplo
    """
    # Municípios do Bié
    municipios = [
        'Kuito', 'Camacupa', 'Catabola', 'Chinguar', 'Chitembo',
        'Cuemba', 'Cunhinga', 'Nharea', 'Andulo'
    ]
    
    # Gerar dados para as últimas 52 semanas
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=52)
    
    data = []
    
    for municipio in municipios:
        # Parâmetros base por município
        if municipio == 'Kuito':
            casos_base = 150
            chuva_base = 120.0
            temp_base = 22.5
        elif municipio == 'Camacupa':
            casos_base = 80
            chuva_base = 100.0
            temp_base = 23.0
        elif municipio == 'Andulo':
            casos_base = 90
            chuva_base = 110.0
            temp_base = 22.0
        else:
            casos_base = 50
            chuva_base = 90.0
            temp_base = 23.5
        
        # Gerar dados semanais
        current_date = start_date
        while current_date <= end_date:
            # Variação sazonal e aleatória
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * current_date.timetuple().tm_yday / 365)
            random_factor = np.random.normal(1, 0.2)
            
            casos = max(0, int(casos_base * seasonal_factor * random_factor))
            chuva = max(0, chuva_base * np.random.normal(1, 0.3))
            temp_media = temp_base + np.random.normal(0, 2)
            
            data.append({
                'municipio': municipio,
                'data_caso': current_date.strftime('%Y-%m-%d'),
                'casos': casos,
                'chuva_mm': round(chuva, 2),
                'temp_media_c': round(temp_media, 2),
                'temp_min_c': round(temp_media - np.random.uniform(2, 5), 2),
                'temp_max_c': round(temp_media + np.random.uniform(2, 5), 2),
                'umidade_relativa': round(60 + np.random.uniform(-20, 20), 2)
            })
            
            current_date += timedelta(weeks=1)
    
    # Criar DataFrame e salvar
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logger.info(f"Dados de exemplo criados: {output_path} ({len(df)} registros)")


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar dados de exemplo
    create_sample_data()
    
    # Testar carregamento
    loader = DataLoader()
    df = loader.load_and_process_data("sample_data.csv")
    print(f"Dados processados: {len(df)} registros")
    print(df.head())
