#!/bin/bash

# Script para parar o Sistema de Previsão de Risco de Malária (Bié)
# Uso: ./scripts/stop.sh

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

echo "🛑 Parando Sistema de Previsão de Risco de Malária (Bié)"
echo "======================================================="

# Parar serviços
print_status "Parando serviços..."
docker-compose -f infra/compose/docker-compose.yaml down

print_success "Serviços parados"

echo ""
echo "✅ Sistema parado com sucesso!"
echo ""
echo "Para iniciar novamente:"
echo "  ./scripts/start.sh"
echo ""
