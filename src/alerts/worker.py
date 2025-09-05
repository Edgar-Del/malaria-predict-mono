"""
Worker para processamento de alertas em background.
"""

import os
import logging
import time
import schedule
from datetime import datetime

from src.alerts.email_sender import EmailAlertSender
from src.ingest.database_manager import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/alerts_worker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AlertsWorker:
    """Worker para processamento de alertas."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.email_sender = EmailAlertSender()
        self.running = False
        
    def check_connection(self) -> bool:
        """Verifica conexão com banco de dados."""
        try:
            return self.db_manager.test_connection()
        except Exception as e:
            logger.error(f"Erro na conexão com banco: {e}")
            return False
    
    def process_alerts(self):
        """Processa alertas e envia notificações."""
        try:
            logger.info("Iniciando processamento de alertas")
            
            # Verificar conexão
            if not self.check_connection():
                logger.error("Não foi possível conectar com o banco de dados")
                return False
            
            # Processar alertas
            success = self.email_sender.check_and_send_alerts(self.db_manager)
                
                if success:
                logger.info("Processamento de alertas concluído com sucesso")
            else:
                logger.warning("Alguns alertas podem não ter sido processados")
            
            return success
                
        except Exception as e:
            logger.error(f"Erro no processamento de alertas: {e}")
            return False
    
    def start_scheduler(self):
        """Inicia o agendador de tarefas."""
        logger.info("Iniciando agendador de alertas")
        
        # Verificar configurações
        if not self.email_sender.enabled:
            logger.warning("Alertas por e-mail desabilitados. Verifique as configurações SMTP.")
            return
        
        # Agendar tarefas
        check_interval = int(os.getenv('ALERTS_CHECK_INTERVAL_HOURS', '24'))
        
        # Verificação diária
        schedule.every().day.at("18:00").do(self.process_alerts)
        
        # Verificação semanal (domingos)
        schedule.every().sunday.at("18:00").do(self.process_alerts)
        
        # Verificação a cada X horas (configurável)
        if check_interval > 0:
            schedule.every(check_interval).hours.do(self.process_alerts)
        
        # Verificação imediata na inicialização
        logger.info("Executando verificação inicial de alertas")
        self.process_alerts()
        
        # Loop principal
        self.running = True
        logger.info(f"Worker iniciado. Verificações a cada {check_interval}h")
        
            try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except KeyboardInterrupt:
            logger.info("Interrupção recebida. Parando worker...")
            self.running = False
            except Exception as e:
            logger.error(f"Erro no worker: {e}")
            self.running = False
    
    def stop(self):
        """Para o worker."""
        self.running = False
        logger.info("Worker parado")
    
    def run_once(self):
        """Executa processamento uma única vez."""
        logger.info("Executando processamento único de alertas")
        return self.process_alerts()


def main():
    """Função principal do worker."""
    logger.info("=== Iniciando Worker de Alertas ===")
    
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar worker
    worker = AlertsWorker()
    
    # Verificar configurações
    if not worker.email_sender.enabled:
        logger.error("Configurações de e-mail não encontradas. Verifique as variáveis de ambiente:")
        logger.error("- SMTP_HOST")
        logger.error("- SMTP_PORT") 
        logger.error("- SMTP_USER")
        logger.error("- SMTP_PASSWORD")
        logger.error("- ALERT_EMAIL_RECIPIENTS")
        return
    
    # Verificar conexão com banco
    if not worker.check_connection():
        logger.error("Não foi possível conectar com o banco de dados")
        return
    
    # Iniciar worker
    try:
        worker.start_scheduler()
    except Exception as e:
        logger.error(f"Erro fatal no worker: {e}")
    finally:
        worker.stop()
        logger.info("=== Worker finalizado ===")


if __name__ == "__main__":
    main()