# Backend - Sistema de Previsão de Malária - Bié

API REST desenvolvida com FastAPI para o sistema de previsão de risco de malária.

## 🏗️ Arquitetura

```
backend/
├── api/                    # Endpoints da API
│   ├── main.py            # Aplicação principal
│   ├── models.py          # Modelos Pydantic
│   └── routes.py          # Rotas da API
├── core/                  # Lógica de negócio
├── infrastructure/        # Infraestrutura
│   ├── database_manager.py # Gerenciamento do banco
│   ├── alerts/            # Sistema de alertas
│   └── docker/            # Configurações Docker
├── shared/                # Código compartilhado
├── tests/                 # Testes automatizados
└── requirements.txt       # Dependências Python
```

## 🚀 Instalação e Execução

### Desenvolvimento Local

```bash
# Instalar dependências
make install

# Executar em modo desenvolvimento
make dev

# Executar testes
make test

# Verificar qualidade do código
make check
```

### Docker

```bash
# Construir imagem
docker build -t malaria-backend .

# Executar container
docker run -p 8000:8000 malaria-backend
```

## 📚 API Endpoints

### Principais Endpoints

- `GET /` - Informações da API
- `GET /health` - Status da API
- `POST /api/v1/predict` - Previsão para um município
- `GET /api/v1/previsoes/semana/{ano_semana}` - Previsões da semana
- `POST /api/v1/train` - Treinar modelo
- `GET /api/v1/metrics/latest` - Últimas métricas
- `GET /api/v1/municipios` - Lista de municípios

### Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Banco de Dados
DATABASE_URL=postgresql://malaria_user:malaria_pass@localhost:5432/malaria_bie

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Email (Alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=admin@example.com

# Modelo
MODEL_PATH=models/malaria_model.joblib
RANDOM_STATE=42
```

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Testes com cobertura
make test-coverage

# Testes específicos
pytest tests/test_api_models.py -v
```

## 📊 Monitoramento

### Health Checks

- **API Health**: http://localhost:8000/health
- **Database**: Verificação automática de conexão
- **Model**: Verificação de modelo carregado

### Logs

```bash
# Ver logs
make logs

# Logs em tempo real
tail -f logs/api.log
```

## 🔧 Desenvolvimento

### Estrutura de Código

- **API**: Endpoints REST com FastAPI
- **Models**: Validação com Pydantic
- **Database**: ORM com SQLAlchemy
- **Alerts**: Sistema de notificações por email
- **Tests**: Testes unitários e de integração

### Padrões de Código

- **Python**: PEP 8, Black, Flake8
- **API**: OpenAPI/Swagger
- **Database**: Migrações com Alembic
- **Logs**: Estruturados com Loguru

## 📈 Performance

### Otimizações

- **Connection Pooling**: PostgreSQL
- **Async/Await**: FastAPI
- **Caching**: Redis (opcional)
- **Rate Limiting**: Proteção contra abuso

### Métricas

- **Requests/sec**: Throughput da API
- **Response Time**: Latência das requisições
- **Error Rate**: Taxa de erro
- **Database**: Queries e conexões

## 🚀 Deploy

### Produção

```bash
# Build da imagem
docker build -t malaria-backend:latest .

# Deploy com docker-compose
docker-compose up -d backend
```

### Variáveis de Produção

```bash
# Produção
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db:5432/malaria_bie
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
