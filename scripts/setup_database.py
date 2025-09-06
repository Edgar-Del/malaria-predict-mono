#!/usr/bin/env python3
"""
Script para configurar o banco de dados do sistema.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingest.database_manager import DatabaseManager
from src.ingest.data_loader import create_sample_data

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Configura o banco de dados e insere dados de exemplo."""
    try:
        logger.info("Iniciando configuração do banco de dados")
        
        # Conectar ao banco
        db_manager = DatabaseManager()
        
        if not db_manager.test_connection():
            logger.error("Falha na conexão com o banco de dados")
            return False
        
        logger.info("Conexão com banco de dados estabelecida")
        
        # Executar scripts SQL
        sql_dir = Path(__file__).parent.parent / "sql"
        
        # Executar script de criação de tabelas
        create_tables_file = sql_dir / "01_create_tables.sql"
        if create_tables_file.exists():
            logger.info("Executando script de criação de tabelas")
            if db_manager.execute_sql_file(str(create_tables_file)):
                logger.info("Tabelas criadas com sucesso")
            else:
                logger.error("Erro ao criar tabelas")
                return False
        
        # Executar script de dados de exemplo
        sample_data_file = sql_dir / "02_sample_data.sql"
        if sample_data_file.exists():
            logger.info("Executando script de dados de exemplo")
            if db_manager.execute_sql_file(str(sample_data_file)):
                logger.info("Dados de exemplo inseridos com sucesso")
            else:
                logger.error("Erro ao inserir dados de exemplo")
                return False
        
        # Criar dados de exemplo adicionais
        logger.info("Criando dados de exemplo adicionais")
        data_dir = Path(__file__).parent.parent / "data" / "raw"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        sample_file = data_dir / "sample_data.csv"
        create_sample_data(str(sample_file))
        
        # Carregar e inserir dados de exemplo
        from src.ingest.data_loader import DataLoader
        loader = DataLoader(str(data_dir))
        df = loader.load_and_process_data("sample_data.csv")
        
        if db_manager.insert_series_semanais(df):
            logger.info("Dados de exemplo inseridos no banco")
        else:
            logger.warning("Erro ao inserir dados de exemplo no banco")
        
        logger.info("Configuração do banco de dados concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro na configuração do banco: {e}")
        return False


def main():
    """Função principal."""
    print("🗄️  Configuração do Banco de Dados - Sistema de Previsão de Malária")
    print("=" * 70)
    
    # Verificar variáveis de ambiente
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
        print("Configure as variáveis no arquivo .env")
        return 1
    
    # Executar configuração
    success = setup_database()
    
    if success:
        print("✅ Banco de dados configurado com sucesso!")
        print("\nPróximos passos:")
        print("1. Execute: python -m src.model.trainer (para treinar o modelo)")
        print("2. Execute: uvicorn src.api.main:app --reload (para iniciar a API)")
        print("3. Execute: cd src/dashboards && npm run dev (para iniciar o dashboard)")
        return 0
    else:
        print("❌ Erro na configuração do banco de dados")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

