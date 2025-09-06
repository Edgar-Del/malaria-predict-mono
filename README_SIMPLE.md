# Sistema de Previsão de Risco de Malária - Bié

Sistema MVP para previsão de risco de malária na província do Bié, Angola, utilizando machine learning e dados climáticos.

## 🎯 Visão Geral

Este sistema fornece previsões semanais de risco de malária (baixo/médio/alto) por município, utilizando:
- **Dados históricos** de casos de malária
- **Dados climáticos** (chuva, temperatura, umidade)
- **Machine Learning** (Random Forest)
- **Dashboard interativo** com mapas e gráficos
- **Sistema de alertas** por email

## 🏗️ Arquitetura

```
malaria_predict/
├── src/
│   ├── api/              # API FastAPI
│   ├── ingest/           # ETL e carregamento de dados
│   ├── features/         # Engenharia de features
│   ├── model/            # Treinamento e predição
│   ├── alerts/           # Sistema de alertas
│   └── dashboards/       # Frontend React/NextJS
├── infra/
│   ├── docker/           # Dockerfiles
│   └── compose/          # docker-compose.yaml
├── sql/                  # Scripts do banco de dados
├── tests/                # Testes automatizados
└── scripts/              # Scripts de utilidade
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Docker e Docker Compose
- Python 3.9+ (para desenvolvimento local)
- Node.js 18+ (para o dashboard)

### Execução Rápida com Docker

```bash
# 1. Clone o repositório
git clone <repository-url>
cd malaria_predict

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Execute o sistema completo
docker-compose up -d

# 4. Acesse os serviços
# Dashboard: http://localhost:3000
# API: http://localhost:8000
# Documentação: http://localhost:8000/docs
```

### Desenvolvimento Local

```bash
# 1. Instalar dependências
pip install -r requirements.txt
cd src/dashboards && npm install

# 2. Configurar banco de dados
python scripts/setup_database.py

# 3. Treinar modelo
python scripts/train_model.py

# 4. Executar sistema
# Terminal 1: API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Dashboard
cd src/dashboards && npm run dev
```

### Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Executar testes
make test

# Formatar código
make format

# Verificar status do sistema
make status

# Parar sistema Docker
make stop-docker
```

## 📊 Funcionalidades

### ✅ Implementado

- **ETL de Dados**: Carregamento e validação de dados históricos
- **Engenharia de Features**: Lags, médias móveis, features sazonais
- **Modelo ML**: Random Forest com validação cruzada
- **API REST**: Endpoints para previsões e métricas
- **Dashboard**: Interface web com mapas e gráficos
- **Sistema de Alertas**: Notificações por email
- **Banco de Dados**: PostgreSQL com schema normalizado
- **Testes**: Testes unitários e de integração
- **Docker**: Containerização completa

### 🎯 Funcionalidades Principais

1. **Previsão de Risco**
   - Classificação em 3 níveis: baixo, médio, alto
   - Score de confiança para cada previsão
   - Probabilidades por classe de risco

2. **Dashboard Interativo**
   - Mapa geográfico com municípios
   - Gráficos de distribuição de risco
   - Tabela de previsões detalhadas
   - Alertas visuais para alto risco

3. **Sistema de Alertas**
   - Verificação automática de alto risco
   - Emails com templates HTML
   - Configuração de thresholds
   - Log de alertas enviados

4. **API REST**
   - Documentação automática (Swagger)
   - Validação de dados com Pydantic
   - Endpoints para previsões e métricas
   - Health checks

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Testes específicos
pytest tests/test_data_loader.py
pytest tests/test_feature_engineering.py
pytest tests/test_api_models.py
pytest tests/test_model_trainer.py

# Testes com cobertura
pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentação da API

A documentação completa da API está disponível em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints Principais

- `GET /` - Informações da API
- `GET /health` - Status da API
- `POST /api/v1/predict` - Previsão para um município
- `GET /api/v1/previsoes/semana/{ano_semana}` - Previsões da semana
- `POST /api/v1/train` - Treinar modelo
- `GET /api/v1/metrics/latest` - Últimas métricas
- `GET /api/v1/municipios` - Lista de municípios

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Banco de Dados
DATABASE_URL=postgresql://malaria_user:malaria_pass@localhost:5432/malaria_bie
POSTGRES_DB=malaria_bie
POSTGRES_USER=malaria_user
POSTGRES_PASSWORD=malaria_pass

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Email (Alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=admin@example.com,user@example.com
ALERT_RISK_THRESHOLD=0.7

# Modelo
MODEL_PATH=models/malaria_model.joblib
RANDOM_STATE=42

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Deploy

### Docker Compose (Recomendado)

```bash
# Produção
docker-compose -f docker-compose.prod.yml up -d

# Desenvolvimento
docker-compose up -d
```

### Manual

```bash
# 1. Configurar banco PostgreSQL
# 2. Instalar dependências Python
pip install -r requirements.txt

# 3. Configurar banco
python scripts/setup_database.py

# 4. Treinar modelo
python scripts/train_model.py

# 5. Executar API
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 6. Executar Dashboard
cd src/dashboards && npm run build && npm start
```

## 📈 Monitoramento

### Health Checks

- **API**: http://localhost:8000/health
- **Dashboard**: http://localhost:3000
- **Banco**: Verificação automática de conexão

### Logs

```bash
# Logs da API
docker-compose logs -f api

# Logs do banco
docker-compose logs -f postgres

# Logs do dashboard
docker-compose logs -f dashboard
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autor

**Edgar Tchissingui**
- Email: edgar@malaria-bie.ao
- GitHub: [@Edgar-Del](https://github.com/Edgar-Del)

## 🎯 Status do Projeto

✅ **MVP Completo** - Sistema funcional com todas as funcionalidades básicas implementadas.

### Próximos Passos

1. **Validação**: Teste com dados reais do Bié
2. **Melhorias**: Baseadas no feedback dos usuários
3. **Expansão**: Extensão para outras províncias
4. **Produção**: Deploy em ambiente de produção

---

**Última Atualização**: Janeiro 2024  
**Versão**: 1.0.0  
**Status**: ✅ MVP Completo

