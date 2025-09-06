"""
Testes unitários para entidades de domínio.
Implementa testes abrangentes para todas as entidades.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.core.domain.entities import (
    Municipality, MunicipalityId, MunicipalityCode, Coordinates,
    RiskPrediction, EpidemiologicalWeek, RiskScore, RiskProbabilities,
    ModelVersion, RiskLevel
)
from src.core.infrastructure.testing.base import EntityTestBase


class TestMunicipalityId(EntityTestBase):
    """Testes para MunicipalityId."""
    
    def test_valid_id(self):
        """Testa criação de ID válido."""
        municipality_id = MunicipalityId(1)
        assert municipality_id.value == 1
    
    def test_invalid_id_zero(self):
        """Testa ID inválido (zero)."""
        with pytest.raises(ValueError, match="Municipality ID must be positive"):
            MunicipalityId(0)
    
    def test_invalid_id_negative(self):
        """Testa ID inválido (negativo)."""
        with pytest.raises(ValueError, match="Municipality ID must be positive"):
            MunicipalityId(-1)


class TestMunicipalityCode(EntityTestBase):
    """Testes para MunicipalityCode."""
    
    def test_valid_code(self):
        """Testa criação de código válido."""
        code = MunicipalityCode("TEST001")
        assert code.value == "TEST001"
    
    def test_empty_code(self):
        """Testa código vazio."""
        with pytest.raises(ValueError, match="Municipality code cannot be empty"):
            MunicipalityCode("")
    
    def test_whitespace_code(self):
        """Testa código com apenas espaços."""
        with pytest.raises(ValueError, match="Municipality code cannot be empty"):
            MunicipalityCode("   ")


class TestCoordinates(EntityTestBase):
    """Testes para Coordinates."""
    
    def test_valid_coordinates(self):
        """Testa coordenadas válidas."""
        coords = Coordinates(
            latitude=Decimal("-12.5"),
            longitude=Decimal("17.0")
        )
        assert coords.latitude == Decimal("-12.5")
        assert coords.longitude == Decimal("17.0")
    
    def test_invalid_latitude_high(self):
        """Testa latitude inválida (muito alta)."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            Coordinates(latitude=Decimal("91"), longitude=Decimal("0"))
    
    def test_invalid_latitude_low(self):
        """Testa latitude inválida (muito baixa)."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            Coordinates(latitude=Decimal("-91"), longitude=Decimal("0"))
    
    def test_invalid_longitude_high(self):
        """Testa longitude inválida (muito alta)."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            Coordinates(latitude=Decimal("0"), longitude=Decimal("181"))
    
    def test_invalid_longitude_low(self):
        """Testa longitude inválida (muito baixa)."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            Coordinates(latitude=Decimal("0"), longitude=Decimal("-181"))


class TestMunicipality(EntityTestBase):
    """Testes para Municipality."""
    
    def test_create_municipality(self):
        """Testa criação de município."""
        municipality = self.create_municipality()
        
        assert municipality.id.value == 1
        assert municipality.name == "Test Municipality"
        assert municipality.code.value == "TEST001"
        assert municipality.population is None
        assert not municipality.is_populated
    
    def test_create_municipality_with_coordinates(self):
        """Testa criação de município com coordenadas."""
        municipality = self.create_municipality(
            latitude=Decimal("-12.5"),
            longitude=Decimal("17.0")
        )
        
        assert municipality.coordinates is not None
        assert municipality.coordinates.latitude == Decimal("-12.5")
        assert municipality.coordinates.longitude == Decimal("17.0")
    
    def test_create_municipality_with_population(self):
        """Testa criação de município com população."""
        municipality = self.create_municipality(population=50000)
        
        assert municipality.population == 50000
        assert municipality.is_populated
    
    def test_empty_name(self):
        """Testa nome vazio."""
        with pytest.raises(ValueError, match="Municipality name cannot be empty"):
            Municipality(
                id=MunicipalityId(1),
                name="",
                code=MunicipalityCode("TEST001")
            )
    
    def test_negative_population(self):
        """Testa população negativa."""
        with pytest.raises(ValueError, match="Population cannot be negative"):
            Municipality(
                id=MunicipalityId(1),
                name="Test",
                code=MunicipalityCode("TEST001"),
                population=-1
            )
    
    def test_population_density(self):
        """Testa cálculo de densidade populacional."""
        municipality = self.create_municipality(
            population=100000,
            latitude=Decimal("-12.5"),
            longitude=Decimal("17.0")
        )
        municipality = Municipality(
            id=municipality.id,
            name=municipality.name,
            code=municipality.code,
            coordinates=municipality.coordinates,
            population=100000,
            area_km2=Decimal("100")
        )
        
        density = municipality.population_density
        assert density == Decimal("1000")  # 100000 hab / 100 km²
    
    def test_update_population(self):
        """Testa atualização de população."""
        municipality = self.create_municipality(population=50000)
        updated = municipality.update_population(75000)
        
        assert updated.population == 75000
        assert updated.updated_at is not None
        assert updated.id == municipality.id  # ID não muda


class TestEpidemiologicalWeek(EntityTestBase):
    """Testes para EpidemiologicalWeek."""
    
    def test_valid_week(self):
        """Testa semana válida."""
        week = EpidemiologicalWeek(year=2024, week=1)
        assert week.year == 2024
        assert week.week == 1
        assert week.formatted == "2024-01"
    
    def test_invalid_week_zero(self):
        """Testa semana inválida (zero)."""
        with pytest.raises(ValueError, match="Week must be between 1 and 53"):
            EpidemiologicalWeek(year=2024, week=0)
    
    def test_invalid_week_high(self):
        """Testa semana inválida (muito alta)."""
        with pytest.raises(ValueError, match="Week must be between 1 and 53"):
            EpidemiologicalWeek(year=2024, week=54)
    
    def test_invalid_year(self):
        """Testa ano inválido."""
        with pytest.raises(ValueError, match="Year must be 2000 or later"):
            EpidemiologicalWeek(year=1999, week=1)
    
    def test_from_string(self):
        """Testa criação a partir de string."""
        week = EpidemiologicalWeek.from_string("2024-01")
        assert week.year == 2024
        assert week.week == 1
    
    def test_from_string_invalid_format(self):
        """Testa string com formato inválido."""
        with pytest.raises(ValueError, match="Invalid week format"):
            EpidemiologicalWeek.from_string("2024-1")  # Sem zero à esquerda


class TestRiskScore(EntityTestBase):
    """Testes para RiskScore."""
    
    def test_valid_score(self):
        """Testa score válido."""
        score = RiskScore(Decimal("0.5"))
        assert score.value == Decimal("0.5")
        assert score.level == RiskLevel.MEDIUM
    
    def test_invalid_score_negative(self):
        """Testa score inválido (negativo)."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 1"):
            RiskScore(Decimal("-0.1"))
    
    def test_invalid_score_high(self):
        """Testa score inválido (muito alto)."""
        with pytest.raises(ValueError, match="Risk score must be between 0 and 1"):
            RiskScore(Decimal("1.1"))
    
    def test_risk_levels(self):
        """Testa níveis de risco."""
        # Baixo risco
        low_score = RiskScore(Decimal("0.3"))
        assert low_score.level == RiskLevel.LOW
        assert low_score.is_low_risk
        assert not low_score.is_medium_risk
        assert not low_score.is_high_risk
        
        # Médio risco
        medium_score = RiskScore(Decimal("0.5"))
        assert medium_score.level == RiskLevel.MEDIUM
        assert not medium_score.is_low_risk
        assert medium_score.is_medium_risk
        assert not medium_score.is_high_risk
        
        # Alto risco
        high_score = RiskScore(Decimal("0.8"))
        assert high_score.level == RiskLevel.HIGH
        assert not high_score.is_low_risk
        assert not high_score.is_medium_risk
        assert high_score.is_high_risk


class TestRiskProbabilities(EntityTestBase):
    """Testes para RiskProbabilities."""
    
    def test_valid_probabilities(self):
        """Testa probabilidades válidas."""
        probs = RiskProbabilities(
            low=Decimal("0.3"),
            medium=Decimal("0.4"),
            high=Decimal("0.3")
        )
        assert probs.low == Decimal("0.3")
        assert probs.medium == Decimal("0.4")
        assert probs.high == Decimal("0.3")
    
    def test_invalid_probability_negative(self):
        """Testa probabilidade negativa."""
        with pytest.raises(ValueError, match="Low probability must be between 0 and 1"):
            RiskProbabilities(
                low=Decimal("-0.1"),
                medium=Decimal("0.5"),
                high=Decimal("0.6")
            )
    
    def test_invalid_probability_high(self):
        """Testa probabilidade muito alta."""
        with pytest.raises(ValueError, match="High probability must be between 0 and 1"):
            RiskProbabilities(
                low=Decimal("0.3"),
                medium=Decimal("0.4"),
                high=Decimal("1.1")
            )
    
    def test_probabilities_dont_sum_to_one(self):
        """Testa probabilidades que não somam 1."""
        with pytest.raises(ValueError, match="Probabilities must sum to approximately 1"):
            RiskProbabilities(
                low=Decimal("0.3"),
                medium=Decimal("0.3"),
                high=Decimal("0.3")
            )
    
    def test_dominant_risk(self):
        """Testa identificação de risco dominante."""
        # Alto risco dominante
        probs_high = RiskProbabilities(
            low=Decimal("0.1"),
            medium=Decimal("0.2"),
            high=Decimal("0.7")
        )
        assert probs_high.dominant_risk == RiskLevel.HIGH
        
        # Médio risco dominante
        probs_medium = RiskProbabilities(
            low=Decimal("0.2"),
            medium=Decimal("0.6"),
            high=Decimal("0.2")
        )
        assert probs_medium.dominant_risk == RiskLevel.MEDIUM
        
        # Baixo risco dominante
        probs_low = RiskProbabilities(
            low=Decimal("0.7"),
            medium=Decimal("0.2"),
            high=Decimal("0.1")
        )
        assert probs_low.dominant_risk == RiskLevel.LOW


class TestModelVersion(EntityTestBase):
    """Testes para ModelVersion."""
    
    def test_valid_version(self):
        """Testa versão válida."""
        version = ModelVersion("v1.0.0")
        assert version.value == "v1.0.0"
        assert version.is_semantic_version
    
    def test_empty_version(self):
        """Testa versão vazia."""
        with pytest.raises(ValueError, match="Model version cannot be empty"):
            ModelVersion("")
    
    def test_semantic_version_detection(self):
        """Testa detecção de versionamento semântico."""
        # Versões válidas
        assert ModelVersion("v1.0.0").is_semantic_version
        assert ModelVersion("1.0.0").is_semantic_version
        assert ModelVersion("2.1.3").is_semantic_version
        
        # Versões inválidas
        assert not ModelVersion("1.0").is_semantic_version
        assert not ModelVersion("v1").is_semantic_version
        assert not ModelVersion("latest").is_semantic_version


class TestRiskPrediction(EntityTestBase):
    """Testes para RiskPrediction."""
    
    def test_create_prediction(self):
        """Testa criação de previsão."""
        prediction = self.create_risk_prediction()
        
        assert prediction.municipality_id.value == 1
        assert prediction.week.formatted == "2024-01"
        assert prediction.risk_score.value == Decimal("0.5")
        assert prediction.model_version.value == "v1.0.0"
    
    def test_risk_level_property(self):
        """Testa propriedade risk_level."""
        prediction = self.create_risk_prediction(risk_score=0.3)
        assert prediction.risk_level == RiskLevel.LOW
        
        prediction = self.create_risk_prediction(risk_score=0.5)
        assert prediction.risk_level == RiskLevel.MEDIUM
        
        prediction = self.create_risk_prediction(risk_score=0.8)
        assert prediction.risk_level == RiskLevel.HIGH
    
    def test_is_alert_worthy(self):
        """Testa se previsão merece alerta."""
        # Alto risco - deve gerar alerta
        prediction_high = self.create_risk_prediction(risk_score=0.8)
        assert prediction_high.is_alert_worthy
        
        # Médio risco com alta probabilidade de alto risco
        prediction_medium = RiskPrediction(
            municipality_id=MunicipalityId(1),
            week=EpidemiologicalWeek.from_string("2024-01"),
            risk_score=RiskScore(Decimal("0.6")),
            probabilities=RiskProbabilities(
                low=Decimal("0.1"),
                medium=Decimal("0.2"),
                high=Decimal("0.7")
            ),
            model_version=ModelVersion("v1.0.0"),
            created_at=datetime.now()
        )
        assert prediction_medium.is_alert_worthy
        
        # Baixo risco - não deve gerar alerta
        prediction_low = self.create_risk_prediction(risk_score=0.3)
        assert not prediction_low.is_alert_worthy
    
    def test_confidence(self):
        """Testa cálculo de confiança."""
        prediction = self.create_risk_prediction()
        confidence = prediction.confidence
        
        # Confiança deve ser a maior probabilidade
        max_prob = max(
            float(prediction.probabilities.low),
            float(prediction.probabilities.medium),
            float(prediction.probabilities.high)
        )
        assert confidence == Decimal(str(max_prob))
    
    def test_to_dict(self):
        """Testa serialização para dicionário."""
        prediction = self.create_risk_prediction()
        data = prediction.to_dict()
        
        assert data['municipality_id'] == 1
        assert data['week'] == "2024-01"
        assert data['risk_level'] == "medio"
        assert data['risk_score'] == 0.5
        assert 'probabilities' in data
        assert 'model_version' in data
        assert 'confidence' in data
        assert 'is_alert_worthy' in data
        assert 'created_at' in data

