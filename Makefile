# Makefile Principal - Sistema de Previsão de Malária - Bié
# Arquitetura: Backend + Frontend + ML + Data

.PHONY: help install dev build start test clean status logs

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)Sistema de Previsão de Malária - Bié$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "Arquitetura:"
	@echo "  Backend: FastAPI + PostgreSQL"
	@echo "  rontend: React/Next.js + TypeScript"
	@echo "  🤖 ML: scikit-learn + MLflow"
	@echo "  📊 Data: ETL + Feature Engineering"
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ==================== INSTALAÇÃO ====================

install: ## Instala todas as dependências
	@echo "$(GREEN)Instalando todas as dependências...$(NC)"
	$(MAKE) install-backend
	$(MAKE) install-frontend
	$(MAKE) install-ml

install-backend: ## Instala dependências do backend
	@echo "$(GREEN)Instalando backend...$(NC)"
	cd backend && $(MAKE) install

install-frontend: ## Instala dependências do frontend
	@echo "$(GREEN)Instalando frontend...$(NC)"
	cd frontend && $(MAKE) install

install-ml: ## Instala dependências do ML
	@echo "$(GREEN)Instalando ML...$(NC)"
	cd ml && $(MAKE) install

# ==================== DESENVOLVIMENTO ====================

dev: ## Executa sistema completo em modo desenvolvimento
	@echo "$(GREEN)Iniciando sistema completo em modo desenvolvimento...$(NC)"
	@echo "Execute em terminais separados:"
	@echo "  Terminal 1: make dev-backend"
	@echo "  Terminal 2: make dev-frontend"
	@echo "  Terminal 3: make dev-ml"
	@echo "  Terminal 4: docker-compose up postgres mlflow"

dev-backend: ## Executa backend em modo desenvolvimento
	@echo "$(GREEN)Iniciando backend...$(NC)"
	cd backend && $(MAKE) dev

dev-frontend: ## Executa frontend em modo desenvolvimento
	@echo "$(GREEN)Iniciando frontend...$(NC)"
	cd frontend && $(MAKE) dev

dev-ml: ## Executa ML em modo desenvolvimento
	@echo "$(GREEN)Iniciando ML...$(NC)"
	cd ml && $(MAKE) dev

# ==================== PRODUÇÃO ====================

build: ## Constrói todos os serviços
	@echo "$(GREEN)Construindo todos os serviços...$(NC)"
	docker-compose build

start: ## Inicia sistema completo
	@echo "$(GREEN)Iniciando sistema completo...$(NC)"
	docker-compose up -d

start-backend: ## Inicia apenas backend
	@echo "$(GREEN)Iniciando backend...$(NC)"
	docker-compose up -d postgres backend

start-frontend: ## Inicia apenas frontend
	@echo "$(GREEN)Iniciando frontend...$(NC)"
	docker-compose up -d frontend

start-ml: ## Inicia apenas ML
	@echo "$(GREEN)Iniciando ML...$(NC)"
	docker-compose up -d postgres mlflow ml-training

# ==================== TESTES ====================

test: ## Executa todos os testes
	@echo "$(GREEN)Executando todos os testes...$(NC)"
	$(MAKE) test-backend
	$(MAKE) test-frontend
	$(MAKE) test-ml

test-backend: ## Executa testes do backend
	@echo "$(GREEN)Testando backend...$(NC)"
	cd backend && $(MAKE) test

test-frontend: ## Executa testes do frontend
	@echo "$(GREEN)Testando frontend...$(NC)"
	cd frontend && $(MAKE) test

test-ml: ## Executa testes do ML
	@echo "$(GREEN)Testando ML...$(NC)"
	cd ml && $(MAKE) test

# ==================== QUALIDADE ====================

lint: ## Executa linter em todos os módulos
	@echo "$(GREEN)Executando linter...$(NC)"
	$(MAKE) lint-backend
	$(MAKE) lint-frontend
	$(MAKE) lint-ml

lint-backend: ## Linter do backend
	cd backend && $(MAKE) lint

lint-frontend: ## Linter do frontend
	cd frontend && $(MAKE) lint

lint-ml: ## Linter do ML
	cd ml && $(MAKE) lint

format: ## Formata código em todos os módulos
	@echo "$(GREEN)Formatando código...$(NC)"
	$(MAKE) format-backend
	$(MAKE) format-frontend
	$(MAKE) format-ml

format-backend: ## Formata backend
	cd backend && $(MAKE) format

format-frontend: ## Formata frontend
	cd frontend && $(MAKE) format

format-ml: ## Formata ML
	cd ml && $(MAKE) format

check: ## Executa verificações completas
	@echo "$(GREEN)Executando verificações completas...$(NC)"
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

# ==================== DOCKER ====================

docker-build: ## Constrói todas as imagens Docker
	@echo "$(GREEN)Construindo imagens Docker...$(NC)"
	docker-compose build

docker-up: ## Inicia todos os serviços com Docker
	@echo "$(GREEN)Iniciando serviços Docker...$(NC)"
	docker-compose up -d

docker-down: ## Para todos os serviços Docker
	@echo "$(GREEN)Parando serviços Docker...$(NC)"
	docker-compose down

docker-logs: ## Mostra logs de todos os serviços
	@echo "$(GREEN)Mostrando logs...$(NC)"
	docker-compose logs -f

docker-clean: ## Limpa containers e volumes Docker
	@echo "$(GREEN)Limpando Docker...$(NC)"
	docker-compose down -v
	docker system prune -f

# ==================== DADOS E ML ====================

data-setup: ## Configura dados iniciais
	@echo "$(GREEN)Configurando dados...$(NC)"
	python scripts/setup_database.py

train-model: ## Treina modelo de ML
	@echo "$(GREEN)Treinando modelo...$(NC)"
	cd ml && $(MAKE) train

ml-pipeline: ## Executa pipeline completo de ML
	@echo "$(GREEN)Executando pipeline ML...$(NC)"
	cd ml && $(MAKE) pipeline

# ==================== MONITORAMENTO ====================

status: ## Verifica status de todos os serviços
	@echo "$(GREEN)Verificando status dos serviços...$(NC)"
	@echo "Backend: $$(curl -s http://localhost:8000/health > /dev/null && echo '$(GREEN)Online$(NC)' || echo '$(RED)Offline$(NC)')"
	@echo "Frontend: $$(curl -s http://localhost:3000 > /dev/null && echo '$(GREEN)Online$(NC)' || echo '$(RED)Offline$(NC)')"
	@echo "MLflow: $$(curl -s http://localhost:5000 > /dev/null && echo '$(GREEN)Online$(NC)' || echo '$(RED)Offline$(NC)')"
	@echo "PostgreSQL: $$(docker-compose ps postgres | grep -q 'Up' && echo '$(GREEN)Online$(NC)' || echo '$(RED)Offline$(NC)')"

logs-backend: ## Mostra logs do backend
	docker-compose logs -f backend

logs-frontend: ## Mostra logs do frontend
	docker-compose logs -f frontend

logs-ml: ## Mostra logs do ML
	docker-compose logs -f ml-training

# ==================== LIMPEZA ====================

clean: ## Limpa arquivos temporários de todos os módulos
	@echo "$(GREEN)Limpando arquivos temporários...$(NC)"
	$(MAKE) clean-backend
	$(MAKE) clean-frontend
	$(MAKE) clean-ml
	rm -rf .coverage htmlcov/ dist/ build/

clean-backend: ## Limpa backend
	cd backend && $(MAKE) clean

clean-frontend: ## Limpa frontend
	cd frontend && $(MAKE) clean

clean-ml: ## Limpa ML
	cd ml && $(MAKE) clean

# ==================== UTILITÁRIOS ====================

quick-start: ## Inicialização rápida do sistema
	@echo "$(GREEN)Inicialização rápida...$(NC)"
	./scripts/quick_start.sh

check-system: ## Verifica saúde do sistema
	@echo "$(GREEN)Verificando sistema...$(NC)"
	python scripts/check_system.py

backup-db: ## Faz backup do banco de dados
	@echo "$(GREEN)Fazendo backup...$(NC)"
	docker-compose exec postgres pg_dump -U malaria_user malaria_bie > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaura backup do banco
	@echo "$(GREEN)Restaurando backup...$(NC)"
	@echo "Uso: make restore-db FILE=backup_file.sql"
	@if [ -z "$(FILE)" ]; then echo "Erro: Especifique o arquivo com FILE=backup_file.sql"; exit 1; fi
	docker-compose exec -T postgres psql -U malaria_user malaria_bie < $(FILE)

# ==================== DESENVOLVIMENTO AVANÇADO ====================

dev-full: ## Setup completo para desenvolvimento
	@echo "$(GREEN)Setup completo para desenvolvimento...$(NC)"
	$(MAKE) install
	$(MAKE) data-setup
	$(MAKE) train-model
	@echo "$(GREEN)Setup concluído! Execute 'make dev' para iniciar$(NC)"

prod-setup: ## Setup para produção
	@echo "$(GREEN)Setup para produção...$(NC)"
	$(MAKE) docker-build
	$(MAKE) docker-up
	@echo "$(GREEN)Setup de produção concluído!$(NC)"

# ==================== INFORMAÇÕES ====================

info: ## Mostra informações do sistema
	@echo "$(GREEN)Informações do Sistema$(NC)"
	@echo "========================"
	@echo "Backend: FastAPI + PostgreSQL"
	@echo "Frontend: React/Next.js + TypeScript"
	@echo "ML: scikit-learn + MLflow"
	@echo "Docker: Multi-container"
	@echo ""
	@echo "Serviços:"
	@echo "  🌐 Dashboard: http://localhost:3000"
	@echo "  🔌 API: http://localhost:8000"
	@echo "  📚 Docs: http://localhost:8000/docs"
	@echo "  🤖 MLflow: http://localhost:5000"
	@echo "  ❤️  Health: http://localhost:8000/health"