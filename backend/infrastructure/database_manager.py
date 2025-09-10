"""
Módulo para gerenciamento de conexões e operações com o banco de dados PostgreSQL.
"""

import os
import logging
from typing import List, Dict, Optional, Any
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Classe para gerenciamento de operações com o banco de dados."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            # Para testes, usar URL padrão
            self.database_url = "postgresql://user:password@localhost:5432/malaria_db"
            logger.warning("DATABASE_URL não configurada - usando URL padrão para testes")
        
        try:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            # Testar conexão
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"Erro ao conectar com banco: {e} - usando modo simulado")
            self.engine = None
            self.SessionLocal = None
    
    @contextmanager
    def get_session(self):
        """Context manager para sessões do banco de dados."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados.
        
        Returns:
            True se conectado com sucesso, False caso contrário
        """
        try:
            if self.engine is None:
                logger.warning("Banco de dados não disponível - usando modo simulado")
                return True
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexão com banco de dados estabelecida")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar com banco de dados: {e}")
            return False
    
    def execute_sql_file(self, file_path: str) -> bool:
        """
        Executa um arquivo SQL.
        
        Args:
            file_path: Caminho para o arquivo SQL
            
        Returns:
            True se executado com sucesso, False caso contrário
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(sql_content))
                conn.commit()
            
            logger.info(f"Arquivo SQL executado: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao executar arquivo SQL {file_path}: {e}")
            return False
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, 
                        if_exists: str = 'append') -> bool:
        """
        Insere um DataFrame no banco de dados.
        
        Args:
            df: DataFrame para inserir
            table_name: Nome da tabela
            if_exists: Comportamento se tabela existir ('append', 'replace', 'fail')
            
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Dados inseridos na tabela {table_name}: {len(df)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir dados na tabela {table_name}: {e}")
            return False
    
    def get_municipios(self) -> List[Dict]:
        """
        Obtém lista de municípios.
        
        Returns:
            Lista de dicionários com dados dos municípios
        """
        try:
            if self.engine is None:
                # Modo simulado - retornar dados de exemplo
                logger.info("Usando dados simulados para municípios")
                return [
                    {
                        'id': 1,
                        'nome': 'Kuito',
                        'cod_ibge_local': 'BIE001',
                        'latitude': -12.3833,
                        'longitude': 16.9333,
                        'populacao': 500000,
                        'area_km2': 2500.0
                    },
                    {
                        'id': 2,
                        'nome': 'Andulo',
                        'cod_ibge_local': 'BIE002',
                        'latitude': -11.4833,
                        'longitude': 16.4167,
                        'populacao': 200000,
                        'area_km2': 1800.0
                    },
                    {
                        'id': 3,
                        'nome': 'Camacupa',
                        'cod_ibge_local': 'BIE003',
                        'latitude': -12.0167,
                        'longitude': 17.4833,
                        'populacao': 150000,
                        'area_km2': 1200.0
                    }
                ]
            
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, nome, cod_ibge_local, latitude, longitude, 
                           populacao, area_km2
                    FROM municipios 
                    ORDER BY nome
                """))
                
                municipios = []
                for row in result:
                    municipios.append({
                        'id': row[0],
                        'nome': row[1],
                        'cod_ibge_local': row[2],
                        'latitude': float(row[3]) if row[3] else None,
                        'longitude': float(row[4]) if row[4] else None,
                        'populacao': row[5],
                        'area_km2': float(row[6]) if row[6] else None
                    })
                
                logger.info(f"Municípios obtidos: {len(municipios)}")
                return municipios
        except Exception as e:
            logger.error(f"Erro ao obter municípios: {e}")
            return []
    
    def get_series_semanais(self, municipio_id: Optional[int] = None, 
                           municipio_nome: Optional[str] = None,
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Obtém dados de séries semanais.
        
        Args:
            municipio_id: ID do município (opcional)
            municipio_nome: Nome do município (opcional)
            limit: Limite de registros (opcional)
            
        Returns:
            DataFrame com dados das séries semanais
        """
        try:
            if self.engine is None:
                # Modo simulado - retornar dados de exemplo
                logger.info("Usando dados simulados para séries semanais")
                import numpy as np
                
                # Dados simulados para os últimos 12 meses
                data = []
                municipios = self.get_municipios()
                
                for municipio in municipios:
                    if municipio_nome and municipio['nome'].lower() != municipio_nome.lower():
                        continue
                    if municipio_id and municipio['id'] != municipio_id:
                        continue
                        
                    # Gerar dados para 52 semanas
                    for week in range(1, 53):
                        # Simular padrão sazonal
                        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * week / 52)
                        base_cases = 10 + np.random.poisson(5)
                        casos = int(base_cases * seasonal_factor)
                        
                        data.append({
                            'municipio_id': municipio['id'],
                            'municipio_nome': municipio['nome'],
                            'ano_semana': f'2024-{week:02d}',
                            'casos': casos,
                            'chuva_mm': np.random.uniform(0, 50),
                            'temp_media_c': np.random.uniform(20, 30),
                            'temp_min_c': np.random.uniform(15, 25),
                            'temp_max_c': np.random.uniform(25, 35),
                            'umidade_relativa': np.random.uniform(40, 90),
                            'casos_lag1': max(0, casos - np.random.randint(0, 3)),
                            'casos_lag2': max(0, casos - np.random.randint(0, 5)),
                            'casos_lag3': max(0, casos - np.random.randint(0, 7)),
                            'casos_lag4': max(0, casos - np.random.randint(0, 9)),
                            'casos_media_2s': casos * 0.9,
                            'casos_media_4s': casos * 0.8
                        })
                
                df = pd.DataFrame(data)
                if limit:
                    df = df.head(limit)
                logger.info(f"Séries semanais simuladas: {len(df)} registros")
                return df
            
            query = """
                SELECT s.*, m.nome as municipio_nome
                FROM series_semanais s
                JOIN municipios m ON s.municipio_id = m.id
            """
            
            params = {}
            if municipio_id:
                query += " WHERE s.municipio_id = :municipio_id"
                params['municipio_id'] = municipio_id
            
            query += " ORDER BY s.municipio_id, s.ano_semana"
            
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql(query, self.engine, params=params)
            logger.info(f"Séries semanais obtidas: {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao obter séries semanais: {e}")
            return pd.DataFrame()
    
    def insert_series_semanais(self, df: pd.DataFrame) -> bool:
        """
        Insere dados de séries semanais.
        
        Args:
            df: DataFrame com dados das séries semanais
            
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            # Mapear nomes de municípios para IDs
            municipios_df = pd.read_sql("SELECT id, nome FROM municipios", self.engine)
            municipio_map = dict(zip(municipios_df['nome'], municipios_df['id']))
            
            # Adicionar municipio_id
            df['municipio_id'] = df['municipio'].map(municipio_map)
            
            # Remover coluna municipio (nome)
            df_clean = df.drop('municipio', axis=1, errors='ignore')
            
            # Inserir dados
            df_clean.to_sql('series_semanais', self.engine, if_exists='append', 
                           index=False, method='multi')
            
            logger.info(f"Séries semanais inseridas: {len(df_clean)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir séries semanais: {e}")
            return False
    
    def get_previsoes(self, ano_semana: Optional[str] = None, 
                     municipio_id: Optional[int] = None) -> pd.DataFrame:
        """
        Obtém previsões.
        
        Args:
            ano_semana: Ano-semana específica (opcional)
            municipio_id: ID do município (opcional)
            
        Returns:
            DataFrame com previsões
        """
        try:
            query = """
                SELECT p.*, m.nome as municipio_nome
                FROM previsoes p
                JOIN municipios m ON p.municipio_id = m.id
            """
            
            conditions = []
            params = {}
            
            if ano_semana:
                conditions.append("p.ano_semana_prevista = :ano_semana")
                params['ano_semana'] = ano_semana
            
            if municipio_id:
                conditions.append("p.municipio_id = :municipio_id")
                params['municipio_id'] = municipio_id
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.municipio_id, p.ano_semana_prevista"
            
            df = pd.read_sql(query, self.engine, params=params)
            logger.info(f"Previsões obtidas: {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao obter previsões: {e}")
            return pd.DataFrame()
    
    def insert_previsoes(self, df: pd.DataFrame) -> bool:
        """
        Insere previsões.
        
        Args:
            df: DataFrame com previsões
            
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            # Mapear nomes de municípios para IDs se necessário
            if 'municipio' in df.columns:
                municipios_df = pd.read_sql("SELECT id, nome FROM municipios", self.engine)
                municipio_map = dict(zip(municipios_df['nome'], municipios_df['id']))
                df['municipio_id'] = df['municipio'].map(municipio_map)
                df = df.drop('municipio', axis=1)
            
            df.to_sql('previsoes', self.engine, if_exists='append', 
                     index=False, method='multi')
            
            logger.info(f"Previsões inseridas: {len(df)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir previsões: {e}")
            return False
    
    def get_metricas_latest(self) -> Optional[Dict]:
        """
        Obtém as últimas métricas do modelo.
        
        Returns:
            Dicionário com métricas ou None se não encontrado
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM metricas_modelo 
                    ORDER BY data_treinamento DESC 
                    LIMIT 1
                """))
                
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return None
    
    def insert_metricas(self, metricas: Dict) -> bool:
        """
        Insere métricas do modelo.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        try:
            df = pd.DataFrame([metricas])
            df.to_sql('metricas_modelo', self.engine, if_exists='append', 
                     index=False)
            
            logger.info("Métricas inseridas com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir métricas: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """
        Remove dados antigos do banco.
        
        Args:
            days_to_keep: Número de dias para manter dados
            
        Returns:
            True se limpeza realizada com sucesso, False caso contrário
        """
        try:
            with self.engine.connect() as conn:
                # Remover previsões antigas
                conn.execute(text("""
                    DELETE FROM previsoes 
                    WHERE created_at < NOW() - INTERVAL '%s days'
                """ % days_to_keep))
                
                # Remover alertas antigos
                conn.execute(text("""
                    DELETE FROM alertas_enviados 
                    WHERE enviado_em < NOW() - INTERVAL '%s days'
                """ % days_to_keep))
                
                conn.commit()
            
            logger.info(f"Limpeza de dados antigos realizada (mantendo {days_to_keep} dias)")
            return True
        except Exception as e:
            logger.error(f"Erro na limpeza de dados: {e}")
            return False


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Testar conexão
    db = DatabaseManager()
    if db.test_connection():
        print("Conexão com banco de dados OK")
        
        # Listar municípios
        municipios = db.get_municipios()
        print(f"Municípios encontrados: {len(municipios)}")
        
        # Obter séries semanais
        series = db.get_series_semanais(limit=10)
        print(f"Séries semanais: {len(series)} registros")
    else:
        print("Erro na conexão com banco de dados")
