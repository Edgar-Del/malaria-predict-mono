"""
Testes para o módulo de alertas.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.alerts.email_sender import EmailAlertSender
from src.alerts.worker import AlertsWorker


class TestEmailAlertSender:
    """Testes para a classe EmailAlertSender."""
    
    @pytest.fixture
    def email_sender(self):
        """Instância do EmailAlertSender para testes."""
        with patch.dict(os.environ, {
            'SMTP_HOST': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'test_password',
            'ALERT_EMAIL_RECIPIENTS': 'gestor1@test.com,gestor2@test.com',
            'ALERT_RISK_THRESHOLD': '0.7',
            'DASHBOARD_URL': 'http://localhost:3000'
        }):
            return EmailAlertSender()
    
    def test_init_with_config(self, email_sender):
        """Testa inicialização com configurações válidas."""
        assert email_sender.smtp_host == 'smtp.test.com'
        assert email_sender.smtp_port == 587
        assert email_sender.smtp_user == 'test@test.com'
        assert email_sender.smtp_password == 'test_password'
        assert email_sender.alert_recipients == ['gestor1@test.com', 'gestor2@test.com']
        assert email_sender.alert_threshold == 0.7
        assert email_sender.enabled == True
    
    def test_init_without_config(self):
        """Testa inicialização sem configurações."""
        with patch.dict(os.environ, {}, clear=True):
            sender = EmailAlertSender()
            assert sender.enabled == False
    
    def test_create_email_content(self, email_sender):
        """Testa criação de conteúdo do e-mail."""
        alert_data = [
            {
                'municipio': 'Kuito',
                'classe_risco': 'alto',
                'score_risco': 0.85,
                'probabilidade_baixo': 0.1,
                'probabilidade_medio': 0.2,
                'probabilidade_alto': 0.7,
                'ano_semana': '2024-01'
            },
            {
                'municipio': 'Camacupa',
                'classe_risco': 'medio',
                'score_risco': 0.65,
                'probabilidade_baixo': 0.2,
                'probabilidade_medio': 0.5,
                'probabilidade_alto': 0.3,
                'ano_semana': '2024-01'
            }
        ]
        
        assunto, html_content, text_content = email_sender._create_email_content(alert_data)
        
        # Verificar assunto
        assert 'ALERTA ALTO' in assunto
        assert '1 município(s) com risco alto' in assunto
        
        # Verificar conteúdo HTML
        assert '<html>' in html_content
        assert 'Kuito' in html_content
        assert 'Camacupa' in html_content
        assert '0.85' in html_content
        assert '0.65' in html_content
        
        # Verificar conteúdo texto
        assert 'ALERTA DE RISCO DE MALÁRIA' in text_content
        assert 'Kuito' in text_content
        assert 'Camacupa' in text_content
    
    @patch('smtplib.SMTP')
    def test_send_alert_email_success(self, mock_smtp, email_sender):
        """Testa envio bem-sucedido de e-mail."""
        # Mock do servidor SMTP
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        alert_data = [
            {
                'municipio': 'Kuito',
                'classe_risco': 'alto',
                'score_risco': 0.85,
                'probabilidade_baixo': 0.1,
                'probabilidade_medio': 0.2,
                'probabilidade_alto': 0.7,
                'ano_semana': '2024-01'
            }
        ]
        
        result = email_sender.send_alert_email(alert_data)
        
        # Verificar se e-mail foi enviado
        assert result == True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_alert_email_failure(self, mock_smtp, email_sender):
        """Testa falha no envio de e-mail."""
        # Mock de erro no servidor SMTP
        mock_smtp.side_effect = Exception("SMTP Error")
        
        alert_data = [
            {
                'municipio': 'Kuito',
                'classe_risco': 'alto',
                'score_risco': 0.85,
                'probabilidade_baixo': 0.1,
                'probabilidade_medio': 0.2,
                'probabilidade_alto': 0.7,
                'ano_semana': '2024-01'
            }
        ]
        
        result = email_sender.send_alert_email(alert_data)
        
        # Verificar se falha foi tratada
        assert result == False
    
    def test_send_alert_email_disabled(self):
        """Testa envio de e-mail com alertas desabilitados."""
        with patch.dict(os.environ, {}, clear=True):
            sender = EmailAlertSender()
            result = sender.send_alert_email([])
            assert result == False
    
    def test_send_alert_email_empty_data(self, email_sender):
        """Testa envio de e-mail com dados vazios."""
        result = email_sender.send_alert_email([])
        assert result == True  # Deve retornar True para dados vazios
    
    @patch('src.alerts.email_sender.datetime')
    def test_check_and_send_alerts(self, mock_datetime, email_sender):
        """Testa verificação e envio de alertas."""
        # Mock da data atual
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        mock_datetime.timedelta.return_value = datetime(2024, 1, 22)
        
        # Mock do banco de dados
        mock_db = Mock()
        mock_previsoes = [
            {
                'municipio_nome': 'Kuito',
                'municipio_id': 1,
                'ano_semana_prevista': '2024-04',
                'classe_risco': 'alto',
                'score_risco': 0.85,
                'probabilidade_baixo': 0.1,
                'probabilidade_medio': 0.2,
                'probabilidade_alto': 0.7
            }
        ]
        mock_db.get_previsoes.return_value = mock_previsoes
        
        # Mock do envio de e-mail
        with patch.object(email_sender, 'send_alert_email', return_value=True):
            result = email_sender.check_and_send_alerts(mock_db)
        
        # Verificar se alertas foram processados
        assert result == True
        mock_db.get_previsoes.assert_called_once()


class TestAlertsWorker:
    """Testes para a classe AlertsWorker."""
    
    @pytest.fixture
    def worker(self):
        """Instância do AlertsWorker para testes."""
        with patch.dict(os.environ, {
            'SMTP_HOST': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'test_password',
            'ALERT_EMAIL_RECIPIENTS': 'gestor1@test.com,gestor2@test.com',
            'ALERT_RISK_THRESHOLD': '0.7',
            'ALERTS_CHECK_INTERVAL_HOURS': '24'
        }):
            return AlertsWorker()
    
    def test_init(self, worker):
        """Testa inicialização do worker."""
        assert worker.db_manager is not None
        assert worker.email_sender is not None
        assert worker.running == False
    
    def test_check_connection_success(self, worker):
        """Testa verificação de conexão bem-sucedida."""
        worker.db_manager.test_connection = Mock(return_value=True)
        
        result = worker.check_connection()
        assert result == True
    
    def test_check_connection_failure(self, worker):
        """Testa verificação de conexão com falha."""
        worker.db_manager.test_connection = Mock(return_value=False)
        
        result = worker.check_connection()
        assert result == False
    
    def test_check_connection_exception(self, worker):
        """Testa verificação de conexão com exceção."""
        worker.db_manager.test_connection = Mock(side_effect=Exception("DB Error"))
        
        result = worker.check_connection()
        assert result == False
    
    @patch('src.alerts.worker.schedule')
    def test_start_scheduler(self, mock_schedule, worker):
        """Testa inicialização do agendador."""
        worker.email_sender.enabled = True
        worker.check_connection = Mock(return_value=True)
        worker.process_alerts = Mock(return_value=True)
        
        # Mock do loop principal
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            try:
                worker.start_scheduler()
            except KeyboardInterrupt:
                pass
        
        # Verificar se tarefas foram agendadas
        assert mock_schedule.every().day.at.called
        assert mock_schedule.every().sunday.at.called
        assert mock_schedule.every().hours.do.called
    
    def test_start_scheduler_disabled(self, worker):
        """Testa inicialização com alertas desabilitados."""
        worker.email_sender.enabled = False
        
        worker.start_scheduler()
        # Deve retornar sem erro
    
    def test_start_scheduler_no_connection(self, worker):
        """Testa inicialização sem conexão com banco."""
        worker.email_sender.enabled = True
        worker.check_connection = Mock(return_value=False)
        
        worker.start_scheduler()
        # Deve retornar sem erro
    
    def test_stop(self, worker):
        """Testa parada do worker."""
        worker.running = True
        worker.stop()
        assert worker.running == False
    
    def test_run_once(self, worker):
        """Testa execução única de processamento."""
        worker.process_alerts = Mock(return_value=True)
        
        result = worker.run_once()
        
        assert result == True
        worker.process_alerts.assert_called_once()


class TestAlertsIntegration:
    """Testes de integração para o sistema de alertas."""
    
    @patch('src.alerts.email_sender.datetime')
    def test_full_alert_flow(self, mock_datetime):
        """Testa fluxo completo de alertas."""
        # Mock da data
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        mock_datetime.timedelta.return_value = datetime(2024, 1, 22)
        
        # Configurar ambiente
        with patch.dict(os.environ, {
            'SMTP_HOST': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'test_password',
            'ALERT_EMAIL_RECIPIENTS': 'gestor1@test.com,gestor2@test.com',
            'ALERT_RISK_THRESHOLD': '0.7'
        }):
            # Criar instâncias
            email_sender = EmailAlertSender()
            worker = AlertsWorker()
            
            # Mock do banco de dados
            mock_previsoes = [
                {
                    'municipio_nome': 'Kuito',
                    'municipio_id': 1,
                    'ano_semana_prevista': '2024-04',
                    'classe_risco': 'alto',
                    'score_risco': 0.85,
                    'probabilidade_baixo': 0.1,
                    'probabilidade_medio': 0.2,
                    'probabilidade_alto': 0.7
                }
            ]
            worker.db_manager.get_previsoes = Mock(return_value=mock_previsoes)
            
            # Mock do envio de e-mail
            with patch.object(email_sender, 'send_alert_email', return_value=True):
                result = worker.process_alerts()
            
            # Verificar se processamento foi bem-sucedido
            assert result == True
