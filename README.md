# Sistema de Previsão de Risco de Malária - Bié

Sistema profissional de previsão de risco de malária para a província do Bié, Angola, desenvolvido com arquitetura de microserviços e machine learning.

## 🏗️ Arquitetura do Projeto

```
malaria_predict/
├── backend/              # API REST (FastAPI + PostgreSQL)
├── frontend/             # Dashboard Web (React/Next.js)
├── ml/                   # Machine Learning (scikit-learn + MLflow)
├── data/                 # Dados e Scripts SQL
├── docs/                 # Documentação
├── scripts/              # Scripts de Utilidade
└── docker-compose.yml    # Orquestração de Serviços
```

## 🎯 Visão Geral

Sistema distribuído que fornece previsões semanais de risco de malária (baixo/médio/alto) por município, utilizando:

- **Dados históricos** de casos de malária
- **Dados climáticos** (chuva, temperatura, umidade)
- **Machine Learning** (Random Forest com validação cruzada)
- **Dashboard interativo** com mapas e gráficos
- **Sistema de alertas** por email automático

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Python 3.9+ (para desenvolvimento local)
- Node.js 18+ (para o frontend)

### Execução com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone <repository-url>
cd malaria_predict

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Execute o sistema completo
make docker-up

# 4. Acesse os serviços
# Dashboard: http://localhost:3000
# API: http://localhost:8000
# MLflow: http://localhost:5000
```

### Desenvolvimento Local

```bash
# Instalação completa
make install

# Executar em modo desenvolvimento
make dev

# Verificar status
make status
```

## 📊 Serviços Disponíveis

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Dashboard** | http://localhost:3000 | Interface web principal |
| **API** | http://localhost:8000 | API REST |
| **Documentação** | http://localhost:8000/docs | Swagger UI |
| **MLflow** | http://localhost:5000 | Tracking de experimentos ML |
| **Health Check** | http://localhost:8000/health | Status da API |

## 🏗️ Módulos do Sistema

### 🖥️ Backend (`/backend`)
API REST desenvolvida com FastAPI para gerenciar previsões e dados.

**Tecnologias:**
- FastAPI + Python 3.9+
- PostgreSQL + SQLAlchemy
- Pydantic para validação
- Sistema de alertas por email

**Funcionalidades:**
- Endpoints REST documentados
- Gerenciamento de dados históricos
- Sistema de alertas automático
- Health checks e monitoramento

### 🌐 Frontend (`/frontend`)
Dashboard web responsivo para visualização de previsões.

**Tecnologias:**
- React 18 + Next.js 14
- TypeScript + Tailwind CSS
- Leaflet para mapas
- Recharts para gráficos

**Funcionalidades:**
- Mapa interativo dos municípios
- Gráficos de distribuição de risco
- Tabelas de previsões detalhadas
- Alertas visuais para alto risco

### 🤖 ML (`/ml`)
Módulo de machine learning para treinamento e predição.

**Tecnologias:**
- scikit-learn + pandas + numpy
- MLflow para experimentos
- Feature engineering avançado
- Validação cruzada estratificada

**Funcionalidades:**
- Engenharia de features temporais
- Treinamento de modelos Random Forest
- Validação e avaliação de performance
- Tracking de experimentos com MLflow

## 🔧 Comandos Principais

### Sistema Completo
```bash
make help              # Ver todos os comandos
make install           # Instalar todas as dependências
make dev               # Modo desenvolvimento
make docker-up         # Iniciar com Docker
make status            # Verificar status
make test              # Executar todos os testes
make clean             # Limpar arquivos temporários
```

### Módulos Específicos
```bash
# Backend
make dev-backend       # Executar API
make test-backend      # Testar API
make lint-backend      # Linter do backend

# Frontend
make dev-frontend      # Executar dashboard
make test-frontend     # Testar frontend
make build-frontend    # Build de produção

# ML
make train-model       # Treinar modelo
make ml-pipeline       # Pipeline completo
make mlflow-ui         # Interface MLflow
```

## 📊 Funcionalidades Implementadas

### ✅ MVP Completo
- [x] **ETL Robusto**: Ingestão e validação de dados
- [x] **Engenharia de Features**: Lags, médias móveis, sazonalidade
- [x] **ML Profissional**: Random Forest com validação cruzada
- [x] **API REST**: Endpoints completos com documentação
- [x] **Dashboard Interativo**: React/Next.js com mapas e gráficos
- [x] **Sistema de Alertas**: E-mail automático com templates
- [x] **Banco de Dados**: PostgreSQL com schema normalizado
- [x] **Testes Abrangentes**: Unitários e de integração
- [x] **Docker**: Containerização completa
- [x] **Monitoramento**: Logs estruturados e health checks

### 🎯 Funcionalidades Principais

#### 1. Previsão de Risco Inteligente
- **Modelo ML**: Random Forest com GridSearchCV
- **Features**: Dados históricos + climáticos + sazonais
- **Validação**: Cross-validation estratificada
- **Métricas**: Precision, Recall, F1-Score, Confusion Matrix

#### 2. Dashboard Interativo
- **Mapas**: Visualização geográfica com Leaflet
- **Gráficos**: Recharts para análise temporal
- **Responsivo**: Design mobile-first
- **Tempo Real**: Atualizações automáticas

#### 3. Sistema de Alertas
- **Automático**: Verificação periódica de alto risco
- **E-mail**: Templates HTML com dados contextuais
- **Configurável**: Thresholds e destinatários
- **Auditoria**: Log de todos os alertas enviados

#### 4. API REST Profissional
- **Documentação**: OpenAPI/Swagger automática
- **Validação**: Pydantic com schemas rigorosos
- **Rate Limiting**: Proteção contra abuso
- **Segurança**: CORS, headers de segurança

## 🧪 Testes e Qualidade

### Estratégia de Testes
```bash
# Executar todos os testes
make test

# Testes específicos por módulo
make test-backend
make test-frontend
make test-ml

# Testes com cobertura
make test-coverage
```

### Ferramentas de Qualidade
- **Python**: Black, Flake8, MyPy
- **TypeScript**: ESLint, Prettier
- **Docker**: Multi-stage builds otimizados
- **CI/CD**: GitHub Actions (configurável)

## 📚 Documentação

### Documentação por Módulo
- [Backend](backend/README.md) - API REST e infraestrutura
- [Frontend](frontend/README.md) - Dashboard web
- [ML](ml/README.md) - Machine Learning e experimentos

### Documentação da API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

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

### Desenvolvimento
```bash
make dev-full    # Setup completo para desenvolvimento
```

### Produção
```bash
make prod-setup  # Setup para produção
```

### Docker
```bash
make docker-build    # Construir imagens
make docker-up       # Iniciar serviços
make docker-down     # Parar serviços
```

## 📈 Monitoramento

### Health Checks
- **API**: http://localhost:8000/health
- **Dashboard**: http://localhost:3000
- **MLflow**: http://localhost:5000

### Logs
```bash
make logs-backend    # Logs da API
make logs-frontend   # Logs do dashboard
make logs-ml         # Logs do ML
```

### Status do Sistema
```bash
make status          # Verificar status de todos os serviços
python scripts/check_system.py  # Verificação detalhada
```

## 🤝 Contribuição

### Como Contribuir
1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie** uma branch para sua feature
4. **Implemente** seguindo os padrões
5. **Teste** com cobertura adequada
6. **Documente** suas mudanças
7. **Abra** um Pull Request

### Padrões de Contribuição
- **Commits**: Conventional Commits
- **PRs**: Template obrigatório
- **Testes**: Cobertura mínima 80%
- **Documentação**: Atualizar docs necessárias
- **Code Review**: Revisão obrigatória

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autor

**Edgar Tchissingui**
- Email: edgar@malaria-bie.ao
- GitHub: [@Edgar-Del](https://github.com/Edgar-Del)

## 🎯 Status do Projeto

### ✅ MVP Profissional Completo
- **Arquitetura**: Microserviços bem organizados
- **Funcionalidades**: 100% dos requisitos atendidos
- **Qualidade**: Padrões profissionais aplicados
- **Testes**: Cobertura abrangente
- **Documentação**: Completa e atualizada
- **Docker**: Containerização completa
- **Monitoramento**: Observabilidade implementada

### 🚀 Próximos Passos
1. **Demonstração**: Validação com DPS do Bié
2. **Feedback**: Coleta de requisitos adicionais
3. **Iteração**: Melhorias baseadas no feedback
4. **Escala**: Preparação para produção
5. **Expansão**: Extensão para outras províncias

---

**Status**: ✅ **MVP Profissional Completo** - Pronto para Demonstração e Validação

**Última Atualização**: Janeiro 2024  
**Versão**: 1.0.0  
**Licença**: MIT