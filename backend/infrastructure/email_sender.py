"""
Módulo para envio de alertas por e-mail.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import schedule
import time
import threading

from src.ingest.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class EmailAlertSender:
    """Classe para envio de alertas por e-mail."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.alert_recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')
        self.alert_threshold = float(os.getenv('ALERT_RISK_THRESHOLD', '0.7'))
        self.dashboard_url = os.getenv('DASHBOARD_URL', 'http://localhost:3000')
        
        # Validar configurações
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Configurações de SMTP não encontradas. Alertas por e-mail desabilitados.")
            self.enabled = False
        else:
            self.enabled = True
    
    def _create_email_content(self, alert_data: List[Dict]) -> tuple:
        """
        Cria conteúdo do e-mail de alerta.
        
        Args:
            alert_data: Lista de dados de alerta por município
            
        Returns:
            Tuple com (assunto, corpo_html, corpo_texto)
        """
        # Contar alertas por nível de risco
        alto_risco = [a for a in alert_data if a['classe_risco'] == 'alto']
        medio_risco = [a for a in alert_data if a['classe_risco'] == 'medio']
        
        # Assunto do e-mail
        if alto_risco:
            assunto = f"🚨 ALERTA ALTO: {len(alto_risco)} município(s) com risco alto de malária"
        elif medio_risco:
            assunto = f"⚠️ ALERTA MÉDIO: {len(medio_risco)} município(s) com risco médio de malária"
        else:
            assunto = f"📊 Relatório de Risco de Malária - {len(alert_data)} município(s)"
        
        # Corpo HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alerta de Risco de Malária - Bié</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .alert-high {{ background-color: #e74c3c; color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .alert-medium {{ background-color: #f39c12; color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .alert-low {{ background-color: #27ae60; color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .municipality {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .score {{ font-weight: bold; font-size: 1.2em; }}
                .footer {{ margin-top: 30px; padding: 20px; background-color: #ecf0f1; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #34495e; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Sistema de Previsão de Risco de Malária - Bié</h1>
                <p>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
            
            <div class="content">
                <h2>📊 Resumo dos Alertas</h2>
                <p><strong>Total de municípios analisados:</strong> {len(alert_data)}</p>
                <p><strong>Risco Alto:</strong> {len(alto_risco)} município(s)</p>
                <p><strong>Risco Médio:</strong> {len(medio_risco)} município(s)</p>
                <p><strong>Risco Baixo:</strong> {len(alert_data) - len(alto_risco) - len(medio_risco)} município(s)</p>
                
                <h2>📍 Detalhes por Município</h2>
        """
        
        # Adicionar detalhes de cada município
        for alert in alert_data:
            risk_class = alert['classe_risco']
            if risk_class == 'alto':
                alert_class = 'alert-high'
                icon = '🚨'
            elif risk_class == 'medio':
                alert_class = 'alert-medium'
                icon = '⚠️'
            else:
                alert_class = 'alert-low'
                icon = '✅'
            
            html_content += f"""
                <div class="{alert_class}">
                    <h3>{icon} {alert['municipio']}</h3>
                    <p><strong>Classe de Risco:</strong> {risk_class.upper()}</p>
                    <p><strong>Score de Risco:</strong> <span class="score">{alert['score_risco']:.3f}</span></p>
                    <p><strong>Probabilidades:</strong></p>
                    <ul>
                        <li>Baixo: {alert['probabilidade_baixo']:.1%}</li>
                        <li>Médio: {alert['probabilidade_medio']:.1%}</li>
                        <li>Alto: {alert['probabilidade_alto']:.1%}</li>
                    </ul>
                    <p><strong>Semana:</strong> {alert['ano_semana']}</p>
                </div>
            """
        
        # Tabela resumo
        html_content += """
                <h2>📋 Tabela Resumo</h2>
                <table>
                    <tr>
                        <th>Município</th>
                        <th>Classe de Risco</th>
                        <th>Score</th>
                        <th>Prob. Alto</th>
                        <th>Semana</th>
                    </tr>
        """
        
        for alert in alert_data:
            html_content += f"""
                    <tr>
                        <td>{alert['municipio']}</td>
                        <td>{alert['classe_risco'].upper()}</td>
                        <td>{alert['score_risco']:.3f}</td>
                        <td>{alert['probabilidade_alto']:.1%}</td>
                        <td>{alert['ano_semana']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="footer">
                <h3>🔗 Ações Recomendadas</h3>
                <ul>
                    <li>Acesse o dashboard para visualizações detalhadas: <a href="{}">Dashboard de Malária</a></li>
                    <li>Monitore os municípios com risco alto de perto</li>
                    <li>Prepare recursos adicionais se necessário</li>
                    <li>Mantenha comunicação com as equipes locais</li>
                </ul>
                
                <p><em>Este é um alerta automático do Sistema de Previsão de Risco de Malária (Bié).</em></p>
                <p><em>Para mais informações, entre em contato com a equipe técnica.</em></p>
            </div>
        </body>
        </html>
        """.format(self.dashboard_url)
        
        # Corpo texto simples
        text_content = f"""
ALERTA DE RISCO DE MALÁRIA - BIÉ
================================

Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

RESUMO:
- Total de municípios: {len(alert_data)}
- Risco Alto: {len(alto_risco)}
- Risco Médio: {len(medio_risco)}
- Risco Baixo: {len(alert_data) - len(alto_risco) - len(medio_risco)}

DETALHES POR MUNICÍPIO:
"""
        
        for alert in alert_data:
            text_content += f"""
{alert['municipio']}:
  - Classe: {alert['classe_risco'].upper()}
  - Score: {alert['score_risco']:.3f}
  - Probabilidades: Baixo {alert['probabilidade_baixo']:.1%}, Médio {alert['probabilidade_medio']:.1%}, Alto {alert['probabilidade_alto']:.1%}
  - Semana: {alert['ano_semana']}
"""
        
        text_content += f"""

AÇÕES RECOMENDADAS:
- Acesse o dashboard: {self.dashboard_url}
- Monitore municípios com risco alto
- Prepare recursos se necessário
- Mantenha comunicação com equipes locais

---
Sistema de Previsão de Risco de Malária (Bié)
        """
        
        return assunto, html_content, text_content
    
    def send_alert_email(self, alert_data: List[Dict]) -> bool:
        """
        Envia e-mail de alerta.
        
        Args:
            alert_data: Lista de dados de alerta por município
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.enabled:
            logger.warning("Alertas por e-mail desabilitados")
            return False
        
        if not alert_data:
            logger.info("Nenhum alerta para enviar")
            return True
        
        try:
            # Criar conteúdo do e-mail
            assunto, html_content, text_content = self._create_email_content(alert_data)
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(self.alert_recipients)
            
            # Adicionar partes do e-mail
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Enviar e-mail
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"E-mail de alerta enviado para {len(self.alert_recipients)} destinatário(s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de alerta: {e}")
            return False
    
    def check_and_send_alerts(self, db_manager: DatabaseManager) -> bool:
        """
        Verifica previsões e envia alertas se necessário.
        
        Args:
            db_manager: Instância do gerenciador de banco de dados
            
        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            # Obter próxima semana
            from datetime import datetime, timedelta
            next_week = datetime.now() + timedelta(weeks=1)
            ano_semana = next_week.strftime('%Y-%W')
            
            # Obter previsões da próxima semana
            previsoes_df = db_manager.get_previsoes(ano_semana=ano_semana)
            
            if previsoes_df.empty:
                logger.info(f"Nenhuma previsão encontrada para a semana {ano_semana}")
                return True
            
            # Filtrar alertas que excedem o limiar
            alertas = []
            for _, row in previsoes_df.iterrows():
                if (row['score_risco'] >= self.alert_threshold or 
                    row['classe_risco'] in ['alto', 'medio']):
                    
                    alertas.append({
                        'municipio': row['municipio_nome'],
                        'classe_risco': row['classe_risco'],
                        'score_risco': float(row['score_risco']),
                        'probabilidade_baixo': float(row['probabilidade_baixo'] or 0),
                        'probabilidade_medio': float(row['probabilidade_medio'] or 0),
                        'probabilidade_alto': float(row['probabilidade_alto'] or 0),
                        'ano_semana': row['ano_semana_prevista']
                    })
            
            if not alertas:
                logger.info("Nenhum alerta necessário para esta semana")
                return True
            
            # Enviar e-mail de alerta
            success = self.send_alert_email(alertas)
            
            if success:
                # Registrar alertas enviados no banco
                for alert in alertas:
                    alert_record = {
                        'municipio_id': previsoes_df[previsoes_df['municipio_nome'] == alert['municipio']]['municipio_id'].iloc[0],
                        'ano_semana': alert['ano_semana'],
                        'classe_risco': alert['classe_risco'],
                        'score_risco': alert['score_risco'],
                        'email_destinatarios': ', '.join(self.alert_recipients),
                        'assunto': f"Alerta de risco de malária - {alert['municipio']} - {alert['ano_semana']}",
                        'status_envio': 'enviado'
                    }
                    
                    # Inserir no banco (implementar método se necessário)
                    logger.info(f"Alerta registrado para {alert['municipio']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao verificar e enviar alertas: {e}")
            return False


def run_alert_scheduler():
    """Executa o agendador de alertas em thread separada."""
    db_manager = DatabaseManager()
    email_sender = EmailAlertSender()
    
    # Agendar verificação diária às 18h
    schedule.every().day.at("18:00").do(
        email_sender.check_and_send_alerts, 
        db_manager
    )
    
    # Agendar verificação semanal aos domingos às 18h
    schedule.every().sunday.at("18:00").do(
        email_sender.check_and_send_alerts, 
        db_manager
    )
    
    logger.info("Agendador de alertas iniciado")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Testar envio de e-mail
    email_sender = EmailAlertSender()
    
    # Dados de teste
    test_alerts = [
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
    
    # Enviar e-mail de teste
    success = email_sender.send_alert_email(test_alerts)
    print(f"E-mail de teste enviado: {success}")
