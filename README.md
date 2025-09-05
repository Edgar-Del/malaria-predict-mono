# Sistema Inteligente de Previsão de Risco de Malária (Bié) - MVP

## Visão Geral

Este é um MVP de um sistema de previsão de risco de malária para a província do Bié, Angola. O sistema utiliza dados históricos de casos de malária e dados climáticos para prever o risco semanal (baixo/médio/alto) por município.

## Funcionalidades do MVP

- **Coleta de dados**: Casos históricos por município e dados climáticos básicos
- **Modelo de previsão**: Random Forest para classificação de risco em 3 níveis
- **Dashboard interativo**: Mapa do Bié por município + séries temporais
- **Alertas por e-mail**: Notificações quando risco > limite configurável
- **Armazenamento**: PostgreSQL para histórico de previsões

## Tecnologias

- **Backend**: Python (FastAPI)
- **Modelagem**: scikit-learn (Random Forest)
- **Banco de dados**: PostgreSQL
- **Frontend**: React com NextJS
- **Infraestrutura**: Docker

## Estrutura do Projeto

```
malaria-bie-mvp/
├─ data/
│   ├─ raw/              # CSV originais (casos, clima)
│   ├─ interim/          # dados limpos/intermediários
│   └─ processed/        # features finais por (município, semana)
├─ notebooks/            # EDA e protótipos
├─ src/
│   ├─ ingest/           # ETL: leitura/limpeza/merge
│   ├─ features/         # engenharia de atributos
│   ├─ model/            # treino, validação, persistência
│   ├─ api/              # FastAPI endpoints
│   ├─ dashboards/       # Frontend React
│   └─ alerts/           # envio de e-mails
├─ infra/
│   ├─ docker/           # Dockerfiles
│   └─ compose/          # docker-compose.yaml
├─ sql/                  # schema e migrações (PostgreSQL)
├─ tests/                # testes unit/integration
├─ .env.example
└─ README.md
```

## Instalação e Execução

### Pré-requisitos

- Docker e Docker Compose
- Python 3.9+ (para desenvolvimento local)

### Execução com Docker

1. Clone o repositório
2. Copie `.env.example` para `.env` e configure as variáveis
3. Execute: `docker-compose up -d`

### Desenvolvimento Local

1. Instale as dependências: `pip install -r requirements.txt`
2. Configure o banco PostgreSQL
3. Execute a API: `uvicorn src.api.main:app --reload`
4. Execute o frontend: `cd src/dashboards && npm run dev`

## Uso da API

### Endpoints Principais

- `POST /train`: Retreina o modelo
- `GET /predict?municipio=X&ano_semana=Y`: Obtém previsão
- `GET /previsoes/semana/{ano_semana}`: Previsões da semana
- `GET /metrics/latest`: Últimas métricas do modelo

### Exemplo de Uso

```bash
# Treinar modelo
curl -X POST http://localhost:8000/train

# Obter previsão
curl "http://localhost:8000/predict?municipio=Kuito&ano_semana=2024-01"
```

## Dashboard

Acesse o dashboard em `http://localhost:3000` para visualizar:
- Mapa de risco por município
- Séries temporais de tendência
- Tabela de previsões atuais

## Alertas

O sistema envia alertas por e-mail quando o risco excede o limite configurado. Configure as variáveis de e-mail no arquivo `.env`.

## Limitações do MVP

- Dados de entrada manuais/semiautomáticos
- Modelo baseline simples
- Deploy local/básico
- Sem notificações via Telegram
- Sem indicadores climáticos em tempo real

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob licença MIT.
