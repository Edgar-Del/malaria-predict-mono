"""
Testes para os modelos Pydantic da API.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.api.models import (
    PrevisaoRequest, PrevisaoResponse, PrevisoesSemanaResponse,
    TreinamentoRequest, TreinamentoResponse, MetricasModeloResponse,
    MunicipioResponse, SerieSemanalResponse, AlertaResponse,
    EstatisticasMunicipioResponse, RelatorioSemanalResponse,
    ConfiguracaoAlertaRequest, ConfiguracaoAlertaResponse,
    ClasseRisco, StatusEnvio
)


class TestPrevisaoRequest:
    """Testes para PrevisaoRequest."""
    
    def test_valid_request(self):
        """Testa requisição válida."""
        request = PrevisaoRequest(
            municipio="Kuito",
            ano_semana="2024-01"
        )
        
        assert request.municipio == "Kuito"
        assert request.ano_semana == "2024-01"
    
    def test_invalid_ano_semana_format(self):
        """Testa formato inválido de ano-semana."""
        with pytest.raises(ValidationError):
            PrevisaoRequest(
                municipio="Kuito",
                ano_semana="2024-1"  # Formato inválido
            )
    
    def test_invalid_ano_semana_year(self):
        """Testa ano fora do range válido."""
        with pytest.raises(ValidationError):
            PrevisaoRequest(
                municipio="Kuito",
                ano_semana="2019-01"  # Ano muito antigo
            )
    
    def test_invalid_ano_semana_week(self):
        """Testa semana fora do range válido."""
        with pytest.raises(ValidationError):
            PrevisaoRequest(
                municipio="Kuito",
                ano_semana="2024-54"  # Semana inválida
            )


class TestPrevisaoResponse:
    """Testes para PrevisaoResponse."""
    
    def test_valid_response(self):
        """Testa resposta válida."""
        response = PrevisaoResponse(
            municipio="Kuito",
            ano_semana_prevista="2024-01",
            classe_risco=ClasseRisco.ALTO,
            score_risco=0.85,
            probabilidade_baixo=0.05,
            probabilidade_medio=0.10,
            probabilidade_alto=0.85,
            modelo_versao="v1.0.0",
            modelo_tipo="RandomForest",
            created_at=datetime.now()
        )
        
        assert response.municipio == "Kuito"
        assert response.classe_risco == ClasseRisco.ALTO
        assert response.score_risco == 0.85
    
    def test_invalid_score_risco(self):
        """Testa score de risco inválido."""
        with pytest.raises(ValidationError):
            PrevisaoResponse(
                municipio="Kuito",
                ano_semana_prevista="2024-01",
                classe_risco=ClasseRisco.ALTO,
                score_risco=1.5,  # Score inválido (> 1)
                probabilidade_baixo=0.05,
                probabilidade_medio=0.10,
                probabilidade_alto=0.85,
                modelo_versao="v1.0.0",
                modelo_tipo="RandomForest",
                created_at=datetime.now()
            )


class TestTreinamentoRequest:
    """Testes para TreinamentoRequest."""
    
    def test_valid_request(self):
        """Testa requisição válida."""
        request = TreinamentoRequest(
            municipios=["Kuito", "Camacupa"],
            test_size=0.2,
            random_state=42,
            retreinar=False
        )
        
        assert request.municipios == ["Kuito", "Camacupa"]
        assert request.test_size == 0.2
        assert request.random_state == 42
        assert request.retreinar == False
    
    def test_invalid_test_size(self):
        """Testa test_size inválido."""
        with pytest.raises(ValidationError):
            TreinamentoRequest(
                test_size=0.8  # Muito alto
            )
    
    def test_default_values(self):
        """Testa valores padrão."""
        request = TreinamentoRequest()
        
        assert request.municipios is None
        assert request.test_size == 0.2
        assert request.random_state == 42
        assert request.retreinar == False


class TestMunicipioResponse:
    """Testes para MunicipioResponse."""
    
    def test_valid_response(self):
        """Testa resposta válida."""
        municipio = MunicipioResponse(
            id=1,
            nome="Kuito",
            cod_ibge_local="BIE001",
            latitude=-12.3833,
            longitude=17.0000,
            populacao=185000,
            area_km2=4814.0
        )
        
        assert municipio.id == 1
        assert municipio.nome == "Kuito"
        assert municipio.latitude == -12.3833
    
    def test_optional_fields(self):
        """Testa campos opcionais."""
        municipio = MunicipioResponse(
            id=1,
            nome="Kuito"
        )
        
        assert municipio.id == 1
        assert municipio.nome == "Kuito"
        assert municipio.cod_ibge_local is None
        assert municipio.latitude is None


class TestSerieSemanalResponse:
    """Testes para SerieSemanalResponse."""
    
    def test_valid_response(self):
        """Testa resposta válida."""
        serie = SerieSemanalResponse(
            municipio="Kuito",
            ano_semana="2024-01",
            casos=10,
            chuva_mm=50.0,
            temp_media_c=25.0,
            temp_min_c=20.0,
            temp_max_c=30.0,
            umidade_relativa=70.0,
            casos_lag1=8,
            casos_lag2=5,
            casos_lag3=3,
            casos_lag4=2,
            casos_media_2s=9.0,
            casos_media_4s=8.5
        )
        
        assert serie.municipio == "Kuito"
        assert serie.casos == 10
        assert serie.chuva_mm == 50.0
    
    def test_optional_fields(self):
        """Testa campos opcionais."""
        serie = SerieSemanalResponse(
            municipio="Kuito",
            ano_semana="2024-01",
            casos=10
        )
        
        assert serie.municipio == "Kuito"
        assert serie.casos == 10
        assert serie.chuva_mm is None
        assert serie.temp_media_c is None


class TestMetricasModeloResponse:
    """Testes para MetricasModeloResponse."""
    
    def test_valid_response(self):
        """Testa resposta válida."""
        metricas = MetricasModeloResponse(
            modelo_versao="v1.0.0",
            modelo_tipo="RandomForest",
            data_treinamento=datetime.now(),
            accuracy=0.85,
            precision_macro=0.82,
            recall_macro=0.83,
            f1_macro=0.825,
            precision_baixo=0.88,
            recall_baixo=0.85,
            f1_baixo=0.865,
            precision_medio=0.80,
            recall_medio=0.82,
            f1_medio=0.81,
            precision_alto=0.84,
            recall_alto=0.83,
            f1_alto=0.835,
            parametros={"n_estimators": 100, "max_depth": 10}
        )
        
        assert metricas.modelo_versao == "v1.0.0"
        assert metricas.accuracy == 0.85
        assert metricas.parametros["n_estimators"] == 100


class TestConfiguracaoAlertaRequest:
    """Testes para ConfiguracaoAlertaRequest."""
    
    def test_valid_request(self):
        """Testa requisição válida."""
        config = ConfiguracaoAlertaRequest(
            threshold_alto_risco=0.8,
            threshold_medio_risco=0.5,
            email_destinatarios=["admin@test.com", "user@test.com"],
            enviar_alertas_automaticos=True
        )
        
        assert config.threshold_alto_risco == 0.8
        assert config.threshold_medio_risco == 0.5
        assert len(config.email_destinatarios) == 2
        assert config.enviar_alertas_automaticos == True
    
    def test_invalid_threshold(self):
        """Testa threshold inválido."""
        with pytest.raises(ValidationError):
            ConfiguracaoAlertaRequest(
                threshold_alto_risco=1.5,  # Inválido (> 1)
                email_destinatarios=["admin@test.com"]
            )
    
    def test_default_values(self):
        """Testa valores padrão."""
        config = ConfiguracaoAlertaRequest(
            email_destinatarios=["admin@test.com"]
        )
        
        assert config.threshold_alto_risco == 0.7
        assert config.threshold_medio_risco == 0.4
        assert config.enviar_alertas_automaticos == True


class TestEnums:
    """Testes para enums."""
    
    def test_classe_risco_enum(self):
        """Testa enum ClasseRisco."""
        assert ClasseRisco.BAIXO == "baixo"
        assert ClasseRisco.MEDIO == "medio"
        assert ClasseRisco.ALTO == "alto"
    
    def test_status_envio_enum(self):
        """Testa enum StatusEnvio."""
        assert StatusEnvio.ENVIADO == "enviado"
        assert StatusEnvio.FALHOU == "falhou"
        assert StatusEnvio.PENDENTE == "pendente"


class TestModelValidation:
    """Testes de validação de modelos."""
    
    def test_previsoes_semana_response(self):
        """Testa PrevisoesSemanaResponse."""
        previsoes = [
            PrevisaoResponse(
                municipio="Kuito",
                ano_semana_prevista="2024-01",
                classe_risco=ClasseRisco.ALTO,
                score_risco=0.85,
                probabilidade_baixo=0.05,
                probabilidade_medio=0.10,
                probabilidade_alto=0.85,
                modelo_versao="v1.0.0",
                modelo_tipo="RandomForest",
                created_at=datetime.now()
            )
        ]
        
        response = PrevisoesSemanaResponse(
            ano_semana="2024-01",
            previsoes=previsoes,
            total_municipios=1,
            municipios_alto_risco=1,
            municipios_medio_risco=0,
            municipios_baixo_risco=0
        )
        
        assert response.ano_semana == "2024-01"
        assert len(response.previsoes) == 1
        assert response.total_municipios == 1
    
    def test_relatorio_semanal_response(self):
        """Testa RelatorioSemanalResponse."""
        relatorio = RelatorioSemanalResponse(
            ano_semana="2024-01",
            total_casos_previstos=100,
            municipios_alto_risco=["Kuito"],
            municipios_medio_risco=["Camacupa"],
            municipios_baixo_risco=["Andulo"],
            recomendacoes=["Intensificar prevenção", "Monitorar situação"],
            alertas_enviados=1
        )
        
        assert relatorio.ano_semana == "2024-01"
        assert relatorio.total_casos_previstos == 100
        assert len(relatorio.municipios_alto_risco) == 1
        assert len(relatorio.recomendacoes) == 2

