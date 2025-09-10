"""
Gerenciador de alertas por email.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

class EmailAlertsManager:
    """Gerenciador de alertas por email."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'alerts@malaria-bie.ao')
        self.default_recipients = os.getenv('DEFAULT_RECIPIENTS', 'admin@malaria-bie.ao').split(',')
    
    async def enviar_alertas_semana(
        self,
        previsoes_df,
        ano_semana: str
    ) -> int:
        """
        Envia alertas por email para previsões de alto risco.
        
        Args:
            previsoes_df: DataFrame com previsões
            ano_semana: Ano-semana das previsões
        
        Returns:
            Número de alertas enviados
        """
        try:
            # Filtrar previsões de alto risco
            alto_risco = previsoes_df[previsoes_df['classe_risco'] == 'alto']
            
            if alto_risco.empty:
                logger.info("Nenhum alerta de alto risco para enviar")
                return 0
            
            # Preparar conteúdo do email
            subject = f"🚨 ALERTA MALÁRIA - Semana {ano_semana}"
            body = self._prepare_alert_email(alto_risco, ano_semana)
            
            # Enviar email
            success = await self._send_email(
                subject=subject,
                body=body,
                recipients=self.default_recipients
            )
            
            if success:
                logger.info(f"Alertas enviados com sucesso para {len(alto_risco)} municípios")
                return len(alto_risco)
            else:
                logger.error("Falha ao enviar alertas")
                return 0
                
        except Exception as e:
            logger.error(f"Erro ao enviar alertas: {e}")
            return 0
    
    def _prepare_alert_email(self, alto_risco_df, ano_semana: str) -> str:
        """Prepara o conteúdo do email de alerta."""
        try:
            html_content = f"""
        <html>
        <head>
            <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .municipio {{ background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #dc3545; }}
                    .score {{ font-weight: bold; color: #dc3545; }}
                    .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
                <div class="header">
                    <h1>🚨 ALERTA DE ALTO RISCO DE MALÁRIA</h1>
                    <h2>Semana {ano_semana}</h2>
                </div>
                
                <div class="content">
                    <p><strong>ATENÇÃO:</strong> Detectados <strong>{len(alto_risco_df)}</strong> municípios com alto risco de malária na semana {ano_semana}.</p>
                    
                    <h3>Municípios em Alto Risco:</h3>
            """
            
            for _, row in alto_risco_df.iterrows():
                html_content += f"""
                    <div class="municipio">
                        <strong>{row['municipio_nome']}</strong><br>
                        Score de Risco: <span class="score">{row['score_risco']:.2f}</span><br>
                        Probabilidade Alto: {row['probabilidade_alto']:.2%}
                    </div>
                """
            
            html_content += f"""
                </div>
                
                <div class="footer">
                    <p>Sistema de Previsão de Risco de Malária - Província do Bié</p>
                    <p>Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
        </body>
        </html>
        """
    
            return html_content
            
        except Exception as e:
            logger.error(f"Erro ao preparar email: {e}")
            return f"Alerta de alto risco para {len(alto_risco_df)} municípios na semana {ano_semana}"
    
    async def _send_email(self, subject: str, body: str, recipients: List[str]) -> bool:
        """Envia email."""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("Credenciais SMTP não configuradas - simulando envio")
                return True
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Adicionar corpo HTML
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    async def enviar_relatorio_semanal(
        self,
        relatorio: Dict[str, Any],
        ano_semana: str
    ) -> bool:
        """
        Envia relatório semanal por email.
        
        Args:
            relatorio: Dados do relatório
            ano_semana: Ano-semana do relatório
            
        Returns:
            True se enviado com sucesso
        """
        try:
            subject = f"📊 Relatório Semanal de Malária - {ano_semana}"
            body = self._prepare_weekly_report_email(relatorio, ano_semana)
            
            return await self._send_email(
                subject=subject,
                body=body,
                recipients=self.default_recipients
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório: {e}")
            return False
    
    def _prepare_weekly_report_email(self, relatorio: Dict[str, Any], ano_semana: str) -> str:
        """Prepara o conteúdo do email de relatório semanal."""
        try:
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat-box {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 5px; }}
                    .high-risk {{ color: #dc3545; }}
                    .medium-risk {{ color: #ffc107; }}
                    .low-risk {{ color: #28a745; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Relatório Semanal de Malária</h1>
                    <h2>Semana {ano_semana}</h2>
                </div>
                
                <div class="content">
                    <div class="stats">
                        <div class="stat-box">
                            <h3 class="high-risk">{relatorio.get('municipios_alto_risco', 0)}</h3>
                            <p>Alto Risco</p>
                        </div>
                        <div class="stat-box">
                            <h3 class="medium-risk">{relatorio.get('municipios_medio_risco', 0)}</h3>
                            <p>Médio Risco</p>
                        </div>
                        <div class="stat-box">
                            <h3 class="low-risk">{relatorio.get('municipios_baixo_risco', 0)}</h3>
                            <p>Baixo Risco</p>
                        </div>
                    </div>
                    
                    <h3>Recomendações:</h3>
                    <ul>
            """
            
            for recomendacao in relatorio.get('recomendacoes', []):
                html_content += f"<li>{recomendacao}</li>"
            
            html_content += f"""
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Sistema de Previsão de Risco de Malária - Província do Bié</p>
                    <p>Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Erro ao preparar relatório: {e}")
            return f"Relatório semanal para {ano_semana}"