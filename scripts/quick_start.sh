#!/bin/bash

# Script de inicialização rápida do Sistema de Previsão de Malária - Bié
# Autor: Edgar Tchissingui
# Data: Janeiro 2024

set -e  # Parar em caso de erro

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
        exit 1
    fi
}

# Verificar se arquivo .env existe
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning "Arquivo .env não encontrado. Criando a partir do .env.example..."
        cp .env.example .env
        print_warning "Configure as variáveis no arquivo .env antes de continuar."
        print_warning "Especialmente: DATABASE_URL, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_RECIPIENTS"
        read -p "Pressione Enter para continuar após configurar o .env..."
    fi
}

# Função principal
main() {
    print_header "Sistema de Previsão de Risco de Malária - Bié"
    print_message "Iniciando configuração rápida..."
    
    # Verificações
    check_docker
    check_env_file
    
    print_message "Construindo e iniciando serviços..."
    
    # Parar containers existentes
    docker-compose down 2>/dev/null || true
    
    # Construir e iniciar serviços
    docker-compose up --build -d
    
    print_message "Aguardando serviços ficarem prontos..."
    sleep 10
    
    # Verificar status dos serviços
    print_message "Verificando status dos serviços..."
    
    # Verificar API
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_message "✅ API está rodando em http://localhost:8000"
    else
        print_warning "⚠️  API pode não estar pronta ainda. Aguarde alguns segundos."
    fi
    
    # Verificar Dashboard
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_message "✅ Dashboard está rodando em http://localhost:3000"
    else
        print_warning "⚠️  Dashboard pode não estar pronto ainda. Aguarde alguns segundos."
    fi
    
    # Verificar PostgreSQL
    if docker-compose ps postgres | grep -q "Up"; then
        print_message "✅ PostgreSQL está rodando"
    else
        print_error "❌ PostgreSQL não está rodando"
    fi
    
    print_header "Configuração Concluída!"
    echo ""
    print_message "Serviços disponíveis:"
    echo "  🌐 Dashboard: http://localhost:3000"
    echo "  🔌 API: http://localhost:8000"
    echo "  📚 Documentação: http://localhost:8000/docs"
    echo "  ❤️  Health Check: http://localhost:8000/health"
    echo ""
    print_message "Próximos passos:"
    echo "  1. Acesse o dashboard em http://localhost:3000"
    echo "  2. Configure dados de exemplo se necessário"
    echo "  3. Treine o modelo através da API"
    echo "  4. Teste as previsões"
    echo ""
    print_message "Para parar os serviços: docker-compose down"
    print_message "Para ver logs: docker-compose logs -f"
    echo ""
    print_message "Configuração rápida concluída! 🎉"
}

# Executar função principal
main "$@"

