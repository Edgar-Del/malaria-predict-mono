# Documentação da API - Sistema de Previsão de Risco de Malária (Bié)

## Visão Geral

A API REST fornece acesso programático a todas as funcionalidades do sistema de previsão de malária. Ela é construída com FastAPI e oferece endpoints para consulta de dados, treinamento de modelos e obtenção de previsões.

**URL Base**: `http://localhost:8000` (desenvolvimento)  
**Versão**: 1.0.0  
**Formato**: JSON

## Autenticação

Atualmente, a API não requer autenticação para o MVP. Em produção, implemente autenticação adequada.

## Endpoints

### 1. Informações Gerais

#### GET /
Informações básicas sobre a API.

**Resposta:**
```json
{
  "message": "Sistema de Previsão de Risco de Malária (Bié)",
  "version": "1.0.0",
  "status": "ativo",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /health
Verificação de saúde da API e dependências.

**Resposta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Possíveis:**
- `healthy`: Sistema funcionando normalmente
- `unhealthy`: Problemas detectados

### 2. Municípios

#### GET /municipios
Lista todos os municípios monitorados.

**Resposta:**
```json
{
  "municipios": [
    {
      "id": 1,
      "nome": "Kuito",
      "cod_ibge_local": "BIE001",
      "latitude": -12.3833,
      "longitude": 17.0000,
      "populacao": 185000,
      "area_km2": 4814.0
    }
  ],
  "total": 9
}
```

### 3. Previsões

#### GET /predict
Obtém previsão de risco para um município específico.

**Parâmetros:**
- `municipio` (string, obrigatório): Nome do município
- `ano_semana` (string, obrigatório): Ano-semana no formato YYYY-WW

**Exemplo:**
```bash
GET /predict?municipio=Kuito&ano_semana=2024-01
```

**Resposta:**
```json
{
  "municipio": "Kuito",
  "ano_semana": "2024-01",
  "classe_risco": "alto",
  "score_risco": 0.85,
  "probabilidade_baixo": 0.1,
  "probabilidade_medio": 0.2,
  "probabilidade_alto": 0.7,
  "modelo_versao": "v1.0.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /previsoes/semana/{ano_semana}
Obtém todas as previsões para uma semana específica.

**Parâmetros:**
- `ano_semana` (string, obrigatório): Ano-semana no formato YYYY-WW

**Exemplo:**
```bash
GET /previsoes/semana/2024-01
```

**Resposta:**
```json
{
  "previsoes": [
    {
      "municipio": "Kuito",
      "municipio_id": 1,
      "ano_semana": "2024-01",
      "classe_risco": "alto",
      "score_risco": 0.85,
      "probabilidade_baixo": 0.1,
      "probabilidade_medio": 0.2,
      "probabilidade_alto": 0.7,
      "modelo_versao": "v1.0.0",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 9,
  "ano_semana": "2024-01"
}
```

### 4. Séries Temporais

#### GET /series/{municipio}
Obtém série temporal de um município específico.

**Parâmetros:**
- `municipio` (string, obrigatório): Nome do município
- `limit` (integer, opcional): Número máximo de registros (padrão: 52)

**Exemplo:**
```bash
GET /series/Kuito?limit=26
```

**Resposta:**
```json
{
  "series": [
    {
      "ano_semana": "2023-01",
      "casos": 45,
      "chuva_mm": 120.5,
      "temp_media_c": 23.2,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "municipio": "Kuito",
  "total": 26
}
```

### 5. Modelo e Métricas

#### POST /train
Treina o modelo com dados atuais.

**Resposta:**
```json
{
  "status": "success",
  "modelo_versao": "v20240115_103000",
  "metrics": {
    "accuracy": 0.8234,
    "precision_macro": 0.8156,
    "recall_macro": 0.8201,
    "f1_macro": 0.8178,
    "precision_baixo": 0.8500,
    "recall_baixo": 0.8200,
    "f1_baixo": 0.8348,
    "precision_medio": 0.7800,
    "recall_medio": 0.8100,
    "f1_medio": 0.7949,
    "precision_alto": 0.8200,
    "recall_alto": 0.8300,
    "f1_alto": 0.8250
  },
  "training_time": 45.2,
  "message": "Modelo treinado com sucesso"
}
```

#### GET /metrics/latest
Obtém as últimas métricas do modelo.

**Resposta:**
```json
{
  "modelo_versao": "v20240115_103000",
  "accuracy": 0.8234,
  "precision_macro": 0.8156,
  "recall_macro": 0.8201,
  "f1_macro": 0.8178,
  "precision_baixo": 0.8500,
  "recall_baixo": 0.8200,
  "f1_baixo": 0.8348,
  "precision_medio": 0.7800,
  "recall_medio": 0.8100,
  "f1_medio": 0.7949,
  "precision_alto": 0.8200,
  "recall_alto": 0.8300,
  "f1_alto": 0.8250,
  "data_treinamento": "2024-01-15T10:30:00Z"
}
```

## Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 400 | Bad Request | Parâmetros inválidos ou modelo não treinado |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Erro de validação de dados |
| 500 | Internal Server Error | Erro interno do servidor |

## Exemplos de Uso

### Python

```python
import requests
import json

# URL base da API
BASE_URL = "http://localhost:8000"

# 1. Verificar saúde da API
response = requests.get(f"{BASE_URL}/health")
print("Status:", response.json())

# 2. Listar municípios
response = requests.get(f"{BASE_URL}/municipios")
municipios = response.json()["municipios"]
print(f"Total de municípios: {len(municipios)}")

# 3. Obter previsão para Kuito
response = requests.get(f"{BASE_URL}/predict?municipio=Kuito&ano_semana=2024-01")
previsao = response.json()
print(f"Risco em Kuito: {previsao['classe_risco']} (score: {previsao['score_risco']})")

# 4. Treinar modelo
response = requests.post(f"{BASE_URL}/train")
resultado = response.json()
print(f"Treinamento: {resultado['status']}")

# 5. Obter série temporal
response = requests.get(f"{BASE_URL}/series/Kuito?limit=10")
series = response.json()["series"]
print(f"Série temporal de Kuito: {len(series)} registros")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function exemploUso() {
  try {
    // 1. Verificar saúde
    const health = await axios.get(`${BASE_URL}/health`);
    console.log('Status:', health.data);

    // 2. Listar municípios
    const municipios = await axios.get(`${BASE_URL}/municipios`);
    console.log(`Total de municípios: ${municipios.data.total}`);

    // 3. Obter previsão
    const previsao = await axios.get(`${BASE_URL}/predict?municipio=Kuito&ano_semana=2024-01`);
    console.log(`Risco em Kuito: ${previsao.data.classe_risco}`);

    // 4. Treinar modelo
    const treinamento = await axios.post(`${BASE_URL}/train`);
    console.log(`Treinamento: ${treinamento.data.status}`);

  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
  }
}

exemploUso();
```

### cURL

```bash
# Verificar saúde
curl http://localhost:8000/health

# Listar municípios
curl http://localhost:8000/municipios

# Obter previsão
curl "http://localhost:8000/predict?municipio=Kuito&ano_semana=2024-01"

# Treinar modelo
curl -X POST http://localhost:8000/train

# Obter previsões da semana
curl http://localhost:8000/previsoes/semana/2024-01

# Obter série temporal
curl "http://localhost:8000/series/Kuito?limit=10"
```

## Tratamento de Erros

### Estrutura de Erro Padrão

```json
{
  "detail": "Mensagem de erro específica"
}
```

### Exemplos de Erros

#### Modelo Não Treinado
```json
{
  "detail": "Modelo não treinado. Execute /train primeiro."
}
```

#### Município Não Encontrado
```json
{
  "detail": "Município 'MunicipioInexistente' não encontrado"
}
```

#### Dados Insuficientes
```json
{
  "detail": "Nenhum dado encontrado para treinamento"
}
```

## Limitações e Considerações

### Rate Limiting
- Atualmente sem limitação de taxa
- Em produção, implementar rate limiting adequado

### Tamanho de Resposta
- Máximo de 1000 registros por requisição
- Use parâmetros de paginação quando disponíveis

### Timeout
- Timeout padrão: 30 segundos
- Operações de treinamento podem levar mais tempo

### Dados Sensíveis
- Não exponha dados pessoais de pacientes
- Use apenas dados agregados e anonimizados

## Monitoramento e Logs

### Logs da API
- Logs estruturados em formato JSON
- Níveis: DEBUG, INFO, WARNING, ERROR
- Rotação automática de logs

### Métricas Disponíveis
- Tempo de resposta por endpoint
- Taxa de erro por endpoint
- Uso de recursos do sistema
- Status das dependências

### Alertas
- Falhas de conectividade com banco
- Erros de treinamento do modelo
- Tempo de resposta elevado
- Uso excessivo de recursos

## Changelog

### v1.0.0 (2024-01-15)
- Lançamento inicial do MVP
- Endpoints básicos implementados
- Suporte a previsões semanais
- Dashboard interativo
- Sistema de alertas por e-mail

### Próximas Versões
- v1.1.0: Autenticação e autorização
- v1.2.0: Rate limiting e throttling
- v1.3.0: Cache de respostas
- v2.0.0: API GraphQL
- v2.1.0: WebSockets para atualizações em tempo real
