#!/usr/bin/env python3
"""
Script para treinar o modelo de previsão de malária.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.trainer import ModelTrainer
from src.ingest.database_manager import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_model():
    """Treina o modelo de previsão de malária."""
    try:
        logger.info("Iniciando treinamento do modelo")
        
        # Conectar ao banco
        db_manager = DatabaseManager()
        
        if not db_manager.test_connection():
            logger.error("Falha na conexão com o banco de dados")
            return False
        
        logger.info("Conexão com banco de dados estabelecida")
        
        # Criar treinador
        trainer = ModelTrainer()
        
        # Treinar modelo
        logger.info("Iniciando treinamento do modelo")
        result = trainer.train_model(
            db_manager=db_manager,
            municipios=None,  # Treinar com todos os municípios
            test_size=0.2,
            random_state=42,
            use_hyperparameter_tuning=False,
            model_type='random_forest'
        )
        
        if result['status'] == 'success':
            logger.info("Treinamento concluído com sucesso")
            logger.info(f"Versão do modelo: {result['modelo_versao']}")
            logger.info(f"Tempo de treinamento: {result['tempo_treinamento']:.2f} segundos")
            logger.info(f"Registros de treinamento: {result['registros_treinamento']}")
            logger.info(f"Registros de teste: {result['registros_teste']}")
            
            # Mostrar métricas
            metrics = result['metricas']
            logger.info("Métricas do modelo:")
            logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"  Precision Macro: {metrics['precision_macro']:.4f}")
            logger.info(f"  Recall Macro: {metrics['recall_macro']:.4f}")
            logger.info(f"  F1 Macro: {metrics['f1_macro']:.4f}")
            
            # Mostrar importância das features
            feature_importance = result['feature_importance']
            if feature_importance:
                logger.info("Top 5 features mais importantes:")
                for i, (feature, importance) in enumerate(list(feature_importance.items())[:5]):
                    logger.info(f"  {i+1}. {feature}: {importance:.4f}")
            
            return True
        else:
            logger.error("Falha no treinamento do modelo")
            return False
        
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        return False


def main():
    """Função principal."""
    print("🤖 Treinamento do Modelo - Sistema de Previsão de Malária")
    print("=" * 70)
    
    # Verificar variáveis de ambiente
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
        print("Configure as variáveis no arquivo .env")
        return 1
    
    # Executar treinamento
    success = train_model()
    
    if success:
        print("✅ Modelo treinado com sucesso!")
        print("\nPróximos passos:")
        print("1. Execute: uvicorn src.api.main:app --reload (para iniciar a API)")
        print("2. Execute: cd src/dashboards && npm run dev (para iniciar o dashboard)")
        print("3. Teste as previsões através da API")
        return 0
    else:
        print("❌ Erro no treinamento do modelo")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

