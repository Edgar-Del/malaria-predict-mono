"""
Sistema de alertas por email para o Sistema de Previsão de Risco de Malária.
"""

import os
import smtplib
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from jinja2 import Template

from ..api.models import PrevisaoResponse

logger = logging.getLogger(__name__)


class EmailAlertsManager:
    """Gerenciador de alertas por email."""
    
    def __init__(self):
        # Configurações de email
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        # Configurações de alerta
        self.alert_email_recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')
        self.alert_risk_threshold = float(os.getenv('ALERT_RISK_THRESHOLD', 0.7))
        
        # Remover emails vazios
        self.alert_email_recipients = [email.strip() for email in self.alert_email_recipients if email.strip()]
        
        # Template de email
        self.email_template = self._get_email_template()
    
    def _get_email_template(self) -> str:
        """
        Retorna template HTML para emails de alerta.
        
        Returns:
            String com template HTML
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alerta de Risco de Malária - Bié</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .header { background-color: #d32f2f; color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px; }
                .header h1 { margin: 0; font-size: 24px; }
                .alert-level { padding: 10px; border-radius: 4px; margin: 10px 0; font-weight: bold; }
                .alert-high { background-color: #ffebee; color: #c62828; border-left: 4px solid #d32f2f; }
                .alert-medium { background-color: #fff3e0; color: #ef6c00; border-left: 4px solid #ff9800; }
                .alert-low { background-color: #e8f5e8; color: #2e7d32; border-left: 4px solid #4caf50; }
                .municipality { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
                .municipality h3 { margin: 0 0 10px 0; color: #007bff; }
                .stats { display: flex; justify-content: space-around; margin: 20px 0; }
                .stat-box { text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
                .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
                .stat-label { font-size: 14px; color: #6c757d; }
                .recommendations { background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
                .recommendations h3 { margin: 0 0 10px 0; color: #1976d2; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d; }
                .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
                .table th { background-color: #f8f9fa; font-weight: bold; }
                .risk-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
                .risk-high { background-color: #ffebee; color: #c62828; }
                .risk-medium { background-color: #fff3e0; color: #ef6c00; }
                .risk-low { background-color: #e8f5e8; color: #2e7d32; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Alerta de Risco de Malária - Província do Bié</h1>
                    <p>Relatório de Previsões - Semana {{ ano_semana }}</p>
                </div>
                
                <div class="alert-level alert-{{ nivel_alerta }}">
                    <strong>Nível de Alerta: {{ nivel_alerta.upper() }}</strong>
                    <p>{{ mensagem_alerta }}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{{ total_municipios }}</div>
                        <div class="stat-label">Total de Municípios</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #d32f2f;">{{ municipios_alto_risco }}</div>
                        <div class="stat-label">Alto Risco</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #ff9800;">{{ municipios_medio_risco }}</div>
                        <div class="stat-label">Médio Risco</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #4caf50;">{{ municipios_baixo_risco }}</div>
                        <div class="stat-label">Baixo Risco</div>
                    </div>
                </div>
                
                {% if municipios_alto_risco > 0 %}
                <h2>🏥 Municípios com Alto Risco</h2>
                {% for municipio in previsoes_alto_risco %}
                <div class="municipality">
                    <h3>{{ municipio.municipio }}</h3>
                    <p><strong>Score de Risco:</strong> {{ "%.1f"|format(municipio.score_risco * 100) }}%</p>
                    <p><strong>Probabilidades:</strong></p>
                    <ul>
                        <li>Baixo: {{ "%.1f"|format(municipio.probabilidade_baixo * 100) }}%</li>
                        <li>Médio: {{ "%.1f"|format(municipio.probabilidade_medio * 100) }}%</li>
                        <li>Alto: {{ "%.1f"|format(municipio.probabilidade_alto * 100) }}%</li>
                    </ul>
                </div>
                {% endfor %}
                {% endif %}
                
                <h2>📊 Resumo por Município</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Município</th>
                            <th>Classe de Risco</th>
                            <th>Score</th>
                            <th>Prob. Alto</th>
                            <th>Prob. Médio</th>
                            <th>Prob. Baixo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for previsao in previsoes %}
                        <tr>
                            <td>{{ previsao.municipio }}</td>
                            <td><span class="risk-badge risk-{{ previsao.classe_risco }}">{{ previsao.classe_risco.upper() }}</span></td>
                            <td>{{ "%.1f"|format(previsao.score_risco * 100) }}%</td>
                            <td>{{ "%.1f"|format(previsao.probabilidade_alto * 100) }}%</td>
                            <td>{{ "%.1f"|format(previsao.probabilidade_medio * 100) }}%</td>
                            <td>{{ "%.1f"|format(previsao.probabilidade_baixo * 100) }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="recommendations">
                    <h3>💡 Recomendações</h3>
                    <ul>
                        {% for recomendacao in recomendacoes %}
                        <li>{{ recomendacao }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="footer">
                    <p><strong>Sistema de Previsão de Risco de Malária - Bié</strong></p>
                    <p>Este relatório foi gerado automaticamente em {{ data_geracao }}.</p>
                    <p>Modelo: {{ modelo_versao }} | Tipo: {{ modelo_tipo }}</p>
                    <p>Para mais informações, acesse o dashboard do sistema.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_email_message(self, subject: str, html_content: str, 
                             recipients: List[str]) -> MIMEMultipart:
        """
        Cria mensagem de email.
        
        Args:
            subject: Assunto do email
            html_content: Conteúdo HTML do email
            recipients: Lista de destinatários
            
        Returns:
            Mensagem de email formatada
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = ', '.join(recipients)
        
        # Adicionar conteúdo HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    def _send_email(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """
        Envia email.
        
        Args:
            msg: Mensagem de email
            recipients: Lista de destinatários
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            # Enviar email
            text = msg.as_string()
            server.sendmail(self.smtp_user, recipients, text)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {len(recipients)} destinatários")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _generate_recommendations(self, previsoes: List[PrevisaoResponse]) -> List[str]:
        """
        Gera recomendações baseadas nas previsões.
        
        Args:
            previsoes: Lista de previsões
            
        Returns:
            Lista de recomendações
        """
        recomendacoes = []
        
        # Contar municípios por classe de risco
        alto_risco = sum(1 for p in previsoes if p.classe_risco == 'alto')
        medio_risco = sum(1 for p in previsoes if p.classe_risco == 'medio')
        baixo_risco = sum(1 for p in previsoes if p.classe_risco == 'baixo')
        
        if alto_risco > 0:
            recomendacoes.append(f"Intensificar ações de prevenção em {alto_risco} município(s) com alto risco")
            recomendacoes.append("Distribuir mosquiteiros e repelentes nas áreas de maior risco")
            recomendacoes.append("Aumentar a vigilância epidemiológica")
        
        if medio_risco > 0:
            recomendacoes.append(f"Monitorar de perto {medio_risco} município(s) com risco médio")
            recomendacoes.append("Preparar recursos para possível escalada do risco")
        
        if baixo_risco > 0:
            recomendacoes.append(f"Manter ações preventivas básicas em {baixo_risco} município(s) com baixo risco")
        
        # Recomendações gerais
        recomendacoes.append("Verificar estoque de medicamentos antimaláricos")
        recomendacoes.append("Capacitar equipes de saúde para diagnóstico precoce")
        recomendacoes.append("Promover campanhas de conscientização sobre prevenção")
        
        return recomendacoes
    
    def _determine_alert_level(self, previsoes: List[PrevisaoResponse]) -> Dict[str, Any]:
        """
        Determina o nível de alerta baseado nas previsões.
        
        Args:
            previsoes: Lista de previsões
            
        Returns:
            Dicionário com informações do nível de alerta
        """
        alto_risco = sum(1 for p in previsoes if p.classe_risco == 'alto')
        medio_risco = sum(1 for p in previsoes if p.classe_risco == 'medio')
        total_municipios = len(previsoes)
        
        # Calcular percentual de alto risco
        percentual_alto_risco = (alto_risco / total_municipios) * 100 if total_municipios > 0 else 0
        
        if percentual_alto_risco >= 50:
            nivel = 'alto'
            mensagem = f"ALERTA CRÍTICO: {percentual_alto_risco:.1f}% dos municípios em alto risco!"
        elif percentual_alto_risco >= 25:
            nivel = 'medio'
            mensagem = f"ALERTA MODERADO: {percentual_alto_risco:.1f}% dos municípios em alto risco"
        elif alto_risco > 0:
            nivel = 'baixo'
            mensagem = f"ALERTA BAIXO: {alto_risco} município(s) em alto risco"
        else:
            nivel = 'baixo'
            mensagem = "Situação controlada - nenhum município em alto risco"
        
        return {
            'nivel': nivel,
            'mensagem': mensagem,
            'percentual_alto_risco': percentual_alto_risco
        }
    
    async def enviar_alertas_semana(self, previsoes_df: pd.DataFrame, 
                                   ano_semana: str) -> int:
        """
        Envia alertas por email para previsões de uma semana.
        
        Args:
            previsoes_df: DataFrame com previsões
            ano_semana: Ano-semana das previsões
            
        Returns:
            Número de alertas enviados
        """
        if not self.alert_email_recipients:
            logger.warning("Nenhum destinatário configurado para alertas")
            return 0
        
        try:
            # Converter DataFrame para lista de PrevisaoResponse
            previsoes = []
            for _, row in previsoes_df.iterrows():
                previsao = PrevisaoResponse(
                    municipio=row['municipio_nome'],
                    ano_semana_prevista=row['ano_semana_prevista'],
                    classe_risco=row['classe_risco'],
                    score_risco=float(row['score_risco']),
                    probabilidade_baixo=float(row['probabilidade_baixo']),
                    probabilidade_medio=float(row['probabilidade_medio']),
                    probabilidade_alto=float(row['probabilidade_alto']),
                    modelo_versao=row['modelo_versao'],
                    modelo_tipo=row['modelo_tipo'],
                    created_at=row['created_at']
                )
                previsoes.append(previsao)
            
            # Filtrar apenas previsões de alto risco
            previsoes_alto_risco = [p for p in previsoes if p.classe_risco == 'alto']
            
            if not previsoes_alto_risco:
                logger.info("Nenhuma previsão de alto risco para enviar alerta")
                return 0
            
            # Gerar email
            email_sent = await self.enviar_email_alerta(previsoes, ano_semana)
            
            return 1 if email_sent else 0
            
        except Exception as e:
            logger.error(f"Erro ao enviar alertas da semana: {e}")
            return 0
    
    async def enviar_email_alerta(self, previsoes: List[PrevisaoResponse], 
                                 ano_semana: str) -> bool:
        """
        Envia email de alerta com previsões.
        
        Args:
            previsoes: Lista de previsões
            ano_semana: Ano-semana das previsões
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.alert_email_recipients:
            logger.warning("Nenhum destinatário configurado")
            return False
        
        try:
            # Determinar nível de alerta
            alert_info = self._determine_alert_level(previsoes)
            
            # Filtrar previsões de alto risco
            previsoes_alto_risco = [p for p in previsoes if p.classe_risco == 'alto']
            
            # Gerar recomendações
            recomendacoes = self._generate_recommendations(previsoes)
            
            # Preparar dados para template
            template_data = {
                'ano_semana': ano_semana,
                'nivel_alerta': alert_info['nivel'],
                'mensagem_alerta': alert_info['mensagem'],
                'total_municipios': len(previsoes),
                'municipios_alto_risco': len(previsoes_alto_risco),
                'municipios_medio_risco': sum(1 for p in previsoes if p.classe_risco == 'medio'),
                'municipios_baixo_risco': sum(1 for p in previsoes if p.classe_risco == 'baixo'),
                'previsoes_alto_risco': previsoes_alto_risco,
                'previsoes': previsoes,
                'recomendacoes': recomendacoes,
                'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'modelo_versao': previsoes[0].modelo_versao if previsoes else 'N/A',
                'modelo_tipo': previsoes[0].modelo_tipo if previsoes else 'N/A'
            }
            
            # Renderizar template
            template = Template(self.email_template)
            html_content = template.render(**template_data)
            
            # Criar assunto
            subject = f"🚨 Alerta de Malária - Bié - Semana {ano_semana} - {alert_info['nivel'].upper()}"
            
            # Criar e enviar email
            msg = self._create_email_message(subject, html_content, self.alert_email_recipients)
            success = self._send_email(msg, self.alert_email_recipients)
            
            if success:
                logger.info(f"Email de alerta enviado para semana {ano_semana}")
            else:
                logger.error(f"Falha ao enviar email de alerta para semana {ano_semana}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de alerta: {e}")
            return False
    
    async def enviar_email_teste(self) -> bool:
        """
        Envia email de teste para verificar configuração.
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.alert_email_recipients:
            logger.warning("Nenhum destinatário configurado")
            return False
        
        try:
            # Criar previsão de teste
            previsao_teste = PrevisaoResponse(
                municipio="Kuito",
                ano_semana_prevista="2024-01",
                classe_risco="alto",
                score_risco=0.85,
                probabilidade_baixo=0.05,
                probabilidade_medio=0.10,
                probabilidade_alto=0.85,
                modelo_versao="v1.0.0",
                modelo_tipo="RandomForest",
                created_at=datetime.now()
            )
            
            # Enviar email de teste
            success = await self.enviar_email_alerta([previsao_teste], "2024-01")
            
            if success:
                logger.info("Email de teste enviado com sucesso")
            else:
                logger.error("Falha ao enviar email de teste")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de teste: {e}")
            return False
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Obtém configuração atual do sistema de alertas.
        
        Returns:
            Dicionário com configuração
        """
        return {
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'smtp_user': self.smtp_user,
            'alert_email_recipients': self.alert_email_recipients,
            'alert_risk_threshold': self.alert_risk_threshold,
            'configured': bool(self.smtp_user and self.smtp_password and self.alert_email_recipients)
        }
    
    def test_connection(self) -> bool:
        """
        Testa conexão com servidor SMTP.
        
        Returns:
            True se conexão bem-sucedida, False caso contrário
        """
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            
            logger.info("Conexão SMTP testada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao testar conexão SMTP: {e}")
            return False


def test_email_alerts() -> None:
    """
    Função para testar o sistema de alertas por email.
    """
    import asyncio
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar gerenciador de alertas
    alerts_manager = EmailAlertsManager()
    
    # Verificar configuração
    config = alerts_manager.get_configuration()
    print("Configuração do sistema de alertas:")
    for key, value in config.items():
        if key == 'smtp_password':
            print(f"  {key}: {'*' * len(str(value)) if value else 'Não configurado'}")
        else:
            print(f"  {key}: {value}")
    
    if not config['configured']:
        print("\n⚠️  Sistema de alertas não configurado completamente")
        print("Configure as variáveis de ambiente:")
        print("  - SMTP_HOST")
        print("  - SMTP_PORT")
        print("  - SMTP_USER")
        print("  - SMTP_PASSWORD")
        print("  - ALERT_EMAIL_RECIPIENTS")
        return
    
    # Testar conexão
    print("\n🔗 Testando conexão SMTP...")
    if alerts_manager.test_connection():
        print("✅ Conexão SMTP OK")
    else:
        print("❌ Erro na conexão SMTP")
        return
    
    # Enviar email de teste
    print("\n📧 Enviando email de teste...")
    success = asyncio.run(alerts_manager.enviar_email_teste())
    
    if success:
        print("✅ Email de teste enviado com sucesso")
    else:
        print("❌ Erro ao enviar email de teste")


if __name__ == "__main__":
    test_email_alerts()

