#!/bin/bash

# Script para iniciar o Sistema de Previsão de Risco de Malária (Bié)
# Uso: ./scripts/start.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "🏥 Iniciando Sistema de Previsão de Risco de Malária (Bié)"
echo "=========================================================="

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    print_error "Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    print_warning "Arquivo .env não encontrado. Copiando de env.example..."
    cp env.example .env
    print_warning "Configure o arquivo .env antes de continuar"
fi

# Iniciar serviços
print_status "Iniciando serviços..."

# Parar serviços existentes se estiverem rodando
docker-compose -f infra/compose/docker-compose.yaml down 2>/dev/null || true

# Iniciar serviços
docker-compose -f infra/compose/docker-compose.yaml up -d

print_success "Serviços iniciados"

# Aguardar serviços ficarem prontos
print_status "Aguardando serviços ficarem prontos..."

# Aguardar PostgreSQL
print_status "Aguardando PostgreSQL..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker-compose -f infra/compose/docker-compose.yaml exec -T postgres pg_isready -U malaria_user -d malaria_bie &>/dev/null; then
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    print_error "PostgreSQL não ficou pronto a tempo"
    exit 1
fi

print_success "PostgreSQL está pronto"

# Aguardar API
print_status "Aguardando API..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8000/health &>/dev/null; then
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    print_warning "API não ficou pronta a tempo, mas pode estar funcionando"
else
    print_success "API está pronta"
fi

# Aguardar Dashboard
print_status "Aguardando Dashboard..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:3000 &>/dev/null; then
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    print_warning "Dashboard não ficou pronto a tempo, mas pode estar funcionando"
else
    print_success "Dashboard está pronto"
fi

# Verificar status dos serviços
print_status "Verificando status dos serviços..."
docker-compose -f infra/compose/docker-compose.yaml ps

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo ""
echo "Acesse:"
echo "  📊 Dashboard: http://localhost:3000"
echo "  🔧 API: http://localhost:8000"
echo "  📚 Documentação da API: http://localhost:8000/docs"
echo ""
echo "Comandos úteis:"
echo "  📋 Ver logs: docker-compose -f infra/compose/docker-compose.yaml logs -f"
echo "  🛑 Parar: docker-compose -f infra/compose/docker-compose.yaml down"
echo "  🔄 Reiniciar: docker-compose -f infra/compose/docker-compose.yaml restart"
echo "  📊 Status: docker-compose -f infra/compose/docker-compose.yaml ps"
echo ""

# Verificar se há dados de exemplo
if [ -f "data/raw/sample_data.csv" ]; then
    print_status "Dados de exemplo encontrados. Você pode treinar o modelo:"
    echo "  curl -X POST http://localhost:8000/train"
    echo ""
fi

print_success "Sistema pronto para uso! 🚀"
