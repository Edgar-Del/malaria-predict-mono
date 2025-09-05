# Guia de Instalação - Sistema de Previsão de Risco de Malária (Bié)

## Pré-requisitos

### Sistema Operacional
- Linux (Ubuntu 20.04+ recomendado)
- macOS 10.15+
- Windows 10+ (com WSL2 recomendado)

### Software Necessário
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

### Recursos Mínimos
- CPU: 2 cores
- RAM: 4GB
- Disco: 10GB livres

## Instalação Rápida (Docker)

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/malaria-bie-mvp.git
cd malaria-bie-mvp
```

### 2. Configure as Variáveis de Ambiente
```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:
```bash
# Banco de Dados
DATABASE_URL=postgresql://malaria_user:malaria_pass@postgres:5432/malaria_bie
POSTGRES_DB=malaria_bie
POSTGRES_USER=malaria_user
POSTGRES_PASSWORD=malaria_pass

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=sua-chave-secreta-aqui

# E-mail (para alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
ALERT_EMAIL_RECIPIENTS=gestor1@example.com,gestor2@example.com
ALERT_RISK_THRESHOLD=0.7

# Modelo
MODEL_PATH=models/malaria_model.joblib
RANDOM_STATE=42

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Execute o Sistema
```bash
# Iniciar todos os serviços
docker-compose -f infra/compose/docker-compose.yaml up -d

# Verificar status
docker-compose -f infra/compose/docker-compose.yaml ps
```

### 4. Verificar Instalação
```bash
# Verificar API
curl http://localhost:8000/health

# Verificar Dashboard
curl http://localhost:3000
```

## Instalação para Desenvolvimento

### 1. Instalar Python 3.9+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# macOS (com Homebrew)
brew install python@3.9

# Windows (usar Python.org ou Anaconda)
```

### 2. Criar Ambiente Virtual
```bash
python3.9 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Instalar PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows (usar instalador oficial)
```

### 5. Configurar Banco de Dados
```bash
# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE malaria_bie;
CREATE USER malaria_user WITH PASSWORD 'malaria_pass';
GRANT ALL PRIVILEGES ON DATABASE malaria_bie TO malaria_user;
\q
```

### 6. Executar Migrações
```bash
# Executar scripts SQL
psql -h localhost -U malaria_user -d malaria_bie -f sql/01_create_tables.sql
psql -h localhost -U malaria_user -d malaria_bie -f sql/02_sample_data.sql
```

### 7. Instalar Frontend
```bash
cd src/dashboards
npm install
```

### 8. Executar Aplicações

#### Terminal 1 - API
```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd src/dashboards
npm run dev
```

#### Terminal 3 - Worker de Alertas (opcional)
```bash
cd src/alerts
python worker.py
```

## Verificação da Instalação

### 1. Testar API
```bash
# Health check
curl http://localhost:8000/health

# Listar municípios
curl http://localhost:8000/municipios

# Treinar modelo
curl -X POST http://localhost:8000/train

# Obter previsão
curl "http://localhost:8000/predict?municipio=Kuito&ano_semana=2024-01"
```

### 2. Testar Frontend
- Acesse http://localhost:3000
- Verifique se o mapa carrega
- Teste a seleção de municípios
- Verifique os gráficos

### 3. Executar Testes
```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_api.py -v
pytest tests/test_model.py -v
pytest tests/test_alerts.py -v
```

## Solução de Problemas

### Problema: Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar logs do container
docker-compose logs postgres
```

### Problema: Porta em Uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Parar serviços conflitantes
sudo systemctl stop apache2  # se necessário
```

### Problema: Erro de Permissões
```bash
# Dar permissões corretas
chmod +x scripts/*.sh
sudo chown -R $USER:$USER .
```

### Problema: Dependências Python
```bash
# Atualizar pip
pip install --upgrade pip

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: Dependências Node.js
```bash
# Limpar cache
npm cache clean --force

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install
```

## Configuração de Produção

### 1. Configurar Nginx (opcional)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
    }
}
```

### 2. Configurar SSL (opcional)
```bash
# Usar Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

### 3. Configurar Backup do Banco
```bash
# Script de backup diário
#!/bin/bash
pg_dump -h localhost -U malaria_user malaria_bie > backup_$(date +%Y%m%d).sql
```

### 4. Monitoramento
```bash
# Verificar logs
docker-compose logs -f

# Verificar uso de recursos
docker stats
```

## Próximos Passos

1. **Configurar Dados Reais**: Substituir dados de exemplo por dados reais
2. **Configurar Alertas**: Configurar SMTP para envio de e-mails
3. **Treinar Modelo**: Executar treinamento inicial com dados históricos
4. **Configurar Agendamento**: Configurar cron jobs para atualizações automáticas
5. **Monitoramento**: Implementar sistema de monitoramento e alertas

## Suporte

Para problemas ou dúvidas:
- Consulte a documentação em `docs/`
- Verifique os logs em `logs/`
- Abra uma issue no repositório
- Entre em contato com a equipe técnica
