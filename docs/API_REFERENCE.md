# Referência da API - Sistema de Previsão de Risco de Malária

## Visão Geral

A API REST do Sistema de Previsão de Risco de Malária fornece endpoints para gerenciar municípios, gerar previsões de risco e monitorar o sistema.

**Base URL**: `https://api.malaria-bie.ao/v1`  
**Versão**: 1.0.0  
**Formato**: JSON  
**Autenticação**: Bearer Token (opcional para endpoints públicos)

## Autenticação

### Bearer Token
```http
Authorization: Bearer <seu_token>
```

### Headers Obrigatórios
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid_opcional>
```

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 403 | Acesso negado |
| 404 | Recurso não encontrado |
| 422 | Erro de validação |
| 429 | Rate limit excedido |
| 500 | Erro interno do servidor |

## Resposta Padrão

### Sucesso
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid-1234-5678",
    "version": "1.0.0"
  }
}
```

### Erro
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "municipality_id",
      "message": "Must be a positive integer"
    },
    "request_id": "uuid-1234-5678"
  }
}
```

## Endpoints

### 1. Municípios

#### Listar Municípios
```http
GET /municipalities
```

**Parâmetros de Query:**
- `limit` (int, opcional): Número máximo de resultados (padrão: 100)
- `offset` (int, opcional): Número de resultados para pular (padrão: 0)
- `search` (string, opcional): Buscar por nome ou código

**Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Andulo",
      "code": "AND001",
      "coordinates": {
        "latitude": -11.4167,
        "longitude": 16.4167
      },
      "population": 50000,
      "area_km2": 100.5,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "limit": 100,
    "offset": 0,
    "has_next": false
  }
}
```

#### Obter Município por ID
```http
GET /municipalities/{id}
```

**Parâmetros de Path:**
- `id` (int): ID do município

**Resposta:**
```json
{
  "data": {
    "id": 1,
    "name": "Andulo",
    "code": "AND001",
    "coordinates": {
      "latitude": -11.4167,
      "longitude": 16.4167
    },
    "population": 50000,
    "area_km2": 100.5,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Previsões de Risco

#### Gerar Previsão de Risco
```http
POST /predictions
```

**Corpo da Requisição:**
```json
{
  "municipality_id": 1,
  "week": "2024-03",
  "model_version": "v1.0.0"
}
```

**Resposta:**
```json
{
  "data": {
    "municipality_id": 1,
    "municipality_name": "Andulo",
    "week": "2024-03",
    "risk_level": "medio",
    "risk_score": 0.65,
    "probabilities": {
      "low": 0.2,
      "medium": 0.6,
      "high": 0.2
    },
    "confidence": 0.6,
    "is_alert_worthy": false,
    "model_version": "v1.0.0",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Gerar Previsões em Lote
```http
POST /predictions/batch
```

**Corpo da Requisição:**
```json
{
  "municipality_ids": [1, 2, 3],
  "week": "2024-03",
  "model_version": "v1.0.0"
}
```

**Resposta:**
```json
{
  "data": [
    {
      "municipality_id": 1,
      "municipality_name": "Andulo",
      "week": "2024-03",
      "risk_level": "medio",
      "risk_score": 0.65,
      "probabilities": {
        "low": 0.2,
        "medium": 0.6,
        "high": 0.2
      },
      "confidence": 0.6,
      "is_alert_worthy": false,
      "model_version": "v1.0.0",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 3,
    "successful": 3,
    "failed": 0
  }
}
```

#### Listar Previsões por Semana
```http
GET /predictions/week/{week}
```

**Parâmetros de Path:**
- `week` (string): Semana epidemiológica (formato: YYYY-WW)

**Parâmetros de Query:**
- `risk_level` (string, opcional): Filtrar por nível de risco
- `alert_worthy` (boolean, opcional): Filtrar por alertas

**Resposta:**
```json
{
  "data": [
    {
      "municipality_id": 1,
      "municipality_name": "Andulo",
      "week": "2024-03",
      "risk_level": "medio",
      "risk_score": 0.65,
      "probabilities": {
        "low": 0.2,
        "medium": 0.6,
        "high": 0.2
      },
      "confidence": 0.6,
      "is_alert_worthy": false,
      "model_version": "v1.0.0",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "week": "2024-03",
    "total": 1,
    "risk_distribution": {
      "low": 0,
      "medium": 1,
      "high": 0
    }
  }
}
```

#### Obter Previsão Específica
```http
GET /predictions/{municipality_id}/{week}
```

**Parâmetros de Path:**
- `municipality_id` (int): ID do município
- `week` (string): Semana epidemiológica

**Resposta:**
```json
{
  "data": {
    "municipality_id": 1,
    "municipality_name": "Andulo",
    "week": "2024-03",
    "risk_level": "medio",
    "risk_score": 0.65,
    "probabilities": {
      "low": 0.2,
      "medium": 0.6,
      "high": 0.2
    },
    "confidence": 0.6,
    "is_alert_worthy": false,
    "model_version": "v1.0.0",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Modelo de ML

#### Treinar Modelo
```http
POST /model/train
```

**Corpo da Requisição:**
```json
{
  "model_type": "random_forest",
  "parameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  },
  "validation_split": 0.2
}
```

**Resposta:**
```json
{
  "data": {
    "model_version": "v1.1.0",
    "training_status": "completed",
    "metrics": {
      "accuracy": 0.85,
      "precision": 0.82,
      "recall": 0.78,
      "f1_score": 0.80
    },
    "training_duration": 120.5,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Obter Métricas do Modelo
```http
GET /model/metrics
```

**Parâmetros de Query:**
- `version` (string, opcional): Versão específica do modelo

**Resposta:**
```json
{
  "data": {
    "model_version": "v1.0.0",
    "metrics": {
      "accuracy": 0.85,
      "precision": 0.82,
      "recall": 0.78,
      "f1_score": 0.80,
      "confusion_matrix": {
        "true_negatives": 100,
        "false_positives": 20,
        "false_negatives": 15,
        "true_positives": 80
      }
    },
    "feature_importance": {
      "historical_cases": 0.35,
      "rainfall": 0.25,
      "temperature": 0.20,
      "seasonal_factor": 0.20
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

#### Listar Versões do Modelo
```http
GET /model/versions
```

**Resposta:**
```json
{
  "data": [
    {
      "version": "v1.1.0",
      "status": "active",
      "accuracy": 0.85,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "version": "v1.0.0",
      "status": "deprecated",
      "accuracy": 0.82,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 4. Alertas

#### Listar Alertas
```http
GET /alerts
```

**Parâmetros de Query:**
- `week` (string, opcional): Filtrar por semana
- `status` (string, opcional): Filtrar por status (sent, pending, failed)
- `limit` (int, opcional): Limite de resultados

**Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "municipality_id": 1,
      "municipality_name": "Andulo",
      "week": "2024-03",
      "risk_level": "alto",
      "risk_score": 0.85,
      "status": "sent",
      "recipients": ["health@bie.gov.ao"],
      "sent_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "status_distribution": {
      "sent": 1,
      "pending": 0,
      "failed": 0
    }
  }
}
```

#### Enviar Alerta Manual
```http
POST /alerts/send
```

**Corpo da Requisição:**
```json
{
  "municipality_id": 1,
  "week": "2024-03",
  "recipients": ["health@bie.gov.ao", "emergency@bie.gov.ao"],
  "message": "Alerta personalizado de alto risco"
}
```

**Resposta:**
```json
{
  "data": {
    "alert_id": 1,
    "status": "sent",
    "recipients": ["health@bie.gov.ao", "emergency@bie.gov.ao"],
    "sent_at": "2024-01-15T10:30:00Z"
  }
}
```

### 5. Monitoramento

#### Health Check
```http
GET /health
```

**Resposta:**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "components": {
      "database": {
        "status": "healthy",
        "response_time_ms": 15.2
      },
      "ml_model": {
        "status": "healthy",
        "response_time_ms": 45.8
      },
      "email_service": {
        "status": "healthy",
        "response_time_ms": 120.5
      }
    },
    "summary": {
      "total_components": 3,
      "healthy": 3,
      "unhealthy": 0,
      "degraded": 0
    }
  }
}
```

#### Métricas do Sistema
```http
GET /metrics
```

**Resposta:**
```json
{
  "data": {
    "predictions": {
      "total": 1500,
      "by_risk_level": {
        "low": 800,
        "medium": 500,
        "high": 200
      },
      "alert_worthy": 200
    },
    "municipalities": {
      "total": 9,
      "high_risk": 2
    },
    "model": {
      "accuracy": 0.85,
      "predictions_per_second": 10.5
    },
    "alerts": {
      "sent_total": 200,
      "failed_total": 5
    },
    "api": {
      "requests_total": 5000,
      "errors_total": 25,
      "avg_response_time_ms": 150.5
    }
  }
}
```

## Rate Limiting

A API implementa rate limiting para proteger contra abuso:

- **Global**: 100 requisições por minuto
- **Previsões**: 10 requisições por minuto
- **Treinamento**: 2 requisições por 5 minutos
- **Health Check**: 100 requisições por minuto
- **Métricas**: 20 requisições por minuto

### Headers de Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| `VALIDATION_ERROR` | Erro de validação de dados |
| `ENTITY_NOT_FOUND` | Entidade não encontrada |
| `ENTITY_ALREADY_EXISTS` | Entidade já existe |
| `BUSINESS_RULE_VIOLATION` | Violação de regra de negócio |
| `EXTERNAL_SERVICE_ERROR` | Erro em serviço externo |
| `CONFIGURATION_ERROR` | Erro de configuração |
| `DATA_INTEGRITY_ERROR` | Erro de integridade de dados |
| `RATE_LIMIT_EXCEEDED` | Rate limit excedido |
| `INTERNAL_SERVER_ERROR` | Erro interno do servidor |

## Exemplos de Uso

### Python
```python
import requests

# Gerar previsão
response = requests.post(
    "https://api.malaria-bie.ao/v1/predictions",
    json={
        "municipality_id": 1,
        "week": "2024-03",
        "model_version": "v1.0.0"
    },
    headers={"Authorization": "Bearer seu_token"}
)

prediction = response.json()["data"]
print(f"Risco: {prediction['risk_level']}")
```

### JavaScript
```javascript
// Gerar previsão
const response = await fetch('https://api.malaria-bie.ao/v1/predictions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer seu_token'
  },
  body: JSON.stringify({
    municipality_id: 1,
    week: '2024-03',
    model_version: 'v1.0.0'
  })
});

const prediction = await response.json();
console.log(`Risco: ${prediction.data.risk_level}`);
```

### cURL
```bash
# Gerar previsão
curl -X POST "https://api.malaria-bie.ao/v1/predictions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token" \
  -d '{
    "municipality_id": 1,
    "week": "2024-03",
    "model_version": "v1.0.0"
  }'
```

## Changelog

### v1.0.0 (2024-01-15)
- Versão inicial da API
- Endpoints para municípios e previsões
- Sistema de alertas
- Monitoramento e métricas
- Rate limiting e segurança

