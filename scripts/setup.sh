#!/bin/bash

# Script de configuração inicial do Sistema de Previsão de Risco de Malária (Bié)
# Uso: ./scripts/setup.sh

set -e  # Parar em caso de erro

echo "🏥 Configurando Sistema de Previsão de Risco de Malária (Bié)"
echo "=============================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    print_error "Execute este script no diretório raiz do projeto"
    exit 1
fi

print_status "Verificando pré-requisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Instale Docker primeiro."
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Instale Docker Compose primeiro."
    exit 1
fi

print_success "Pré-requisitos verificados"

# Criar diretórios necessários
print_status "Criando diretórios necessários..."
mkdir -p data/{raw,interim,processed}
mkdir -p models
mkdir -p logs
mkdir -p src/dashboards/.next

print_success "Diretórios criados"

# Configurar arquivo .env se não existir
if [ ! -f ".env" ]; then
    print_status "Criando arquivo .env..."
    cp env.example .env
    print_warning "Configure o arquivo .env com suas configurações antes de continuar"
    print_warning "Especialmente as configurações de SMTP para alertas por e-mail"
else
    print_success "Arquivo .env já existe"
fi

# Verificar se Python está disponível para testes
if command -v python3 &> /dev/null; then
    print_status "Configurando ambiente Python..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Ambiente virtual Python criado"
    fi
    
    # Ativar ambiente virtual e instalar dependências
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependências Python instaladas"
else
    print_warning "Python3 não encontrado. Testes Python não estarão disponíveis"
fi

# Verificar se Node.js está disponível para frontend
if command -v node &> /dev/null; then
    print_status "Configurando frontend..."
    
    cd src/dashboards
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Dependências do frontend instaladas"
    else
        print_success "Dependências do frontend já instaladas"
    fi
    cd ../..
else
    print_warning "Node.js não encontrado. Frontend não estará disponível em desenvolvimento"
fi

# Criar dados de exemplo
print_status "Criando dados de exemplo..."
if command -v python3 &> /dev/null; then
    source venv/bin/activate
    python -c "
from src.ingest.data_loader import create_sample_data
create_sample_data('data/raw/sample_data.csv')
print('Dados de exemplo criados')
"
    print_success "Dados de exemplo criados"
else
    print_warning "Não foi possível criar dados de exemplo (Python não disponível)"
fi

# Verificar configuração do Docker
print_status "Verificando configuração do Docker..."

# Testar se Docker está rodando
if ! docker info &> /dev/null; then
    print_error "Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

print_success "Docker está funcionando"

# Construir imagens Docker
print_status "Construindo imagens Docker..."
docker-compose -f infra/compose/docker-compose.yaml build

print_success "Imagens Docker construídas"

# Executar testes básicos
print_status "Executando testes básicos..."

if command -v python3 &> /dev/null; then
    source venv/bin/activate
    if python -m pytest tests/test_data_loader.py -v --tb=short; then
        print_success "Testes básicos passaram"
    else
        print_warning "Alguns testes falharam, mas a configuração pode estar correta"
    fi
else
    print_warning "Testes não executados (Python não disponível)"
fi

# Mostrar próximos passos
echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env com suas configurações"
echo "2. Inicie o sistema: docker-compose -f infra/compose/docker-compose.yaml up -d"
echo "3. Acesse o dashboard: http://localhost:3000"
echo "4. Acesse a API: http://localhost:8000/docs"
echo ""
echo "Comandos úteis:"
echo "- Ver logs: docker-compose -f infra/compose/docker-compose.yaml logs -f"
echo "- Parar sistema: docker-compose -f infra/compose/docker-compose.yaml down"
echo "- Reiniciar: docker-compose -f infra/compose/docker-compose.yaml restart"
echo ""
echo "Para desenvolvimento:"
echo "- API: cd src/api && uvicorn main:app --reload"
echo "- Frontend: cd src/dashboards && npm run dev"
echo "- Testes: pytest"
echo ""
echo "Documentação:"
echo "- Guia do usuário: docs/USER_GUIDE.md"
echo "- Documentação da API: docs/API.md"
echo "- Guia de instalação: docs/INSTALLATION.md"
echo ""

print_success "Sistema configurado com sucesso! 🚀"