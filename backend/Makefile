# Backend Makefile - Sistema de Previsão de Malária - Bié

.PHONY: help install dev test lint format clean run

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)Backend - Sistema de Previsão de Malária$(NC)"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências Python
	@echo "$(GREEN)Instalando dependências do backend...$(NC)"
	pip install -e .

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(GREEN)Instalando dependências de desenvolvimento...$(NC)"
	pip install -e ".[dev]"

dev: ## Executa a API em modo desenvolvimento
	@echo "$(GREEN)Iniciando API em modo desenvolvimento...$(NC)"
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run: ## Executa a API em modo produção
	@echo "$(GREEN)Iniciando API em modo produção...$(NC)"
	uvicorn api.main:app --host 0.0.0.0 --port 8000

test: ## Executa testes
	@echo "$(GREEN)Executando testes do backend...$(NC)"
	pytest tests/ -v

test-coverage: ## Executa testes com cobertura
	@echo "$(GREEN)Executando testes com cobertura...$(NC)"
	pytest tests/ --cov=api --cov=infrastructure --cov-report=html --cov-report=term

lint: ## Executa linter
	@echo "$(GREEN)Executando linter...$(NC)"
	flake8 api/ infrastructure/ tests/

format: ## Formata código
	@echo "$(GREEN)Formatando código...$(NC)"
	black api/ infrastructure/ tests/
	isort api/ infrastructure/ tests/

check: ## Executa verificações (format + lint + test)
	@echo "$(GREEN)Executando verificações...$(NC)"
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

clean: ## Limpa arquivos temporários
	@echo "$(GREEN)Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .coverage htmlcov/ dist/ build/

migrate: ## Executa migrações do banco
	@echo "$(GREEN)Executando migrações...$(NC)"
	alembic upgrade head

migrate-create: ## Cria nova migração
	@echo "$(GREEN)Criando nova migração...$(NC)"
	@read -p "Nome da migração: " name; \
	alembic revision --autogenerate -m "$$name"

db-init: ## Inicializa banco de dados
	@echo "$(GREEN)Inicializando banco de dados...$(NC)"
	python -c "from infrastructure.database_manager import DatabaseManager; db = DatabaseManager(); db.execute_sql_file('data/sql/01_create_tables.sql')"

logs: ## Mostra logs da API
	@echo "$(GREEN)Mostrando logs...$(NC)"
	tail -f logs/api.log

health: ## Verifica saúde da API
	@echo "$(GREEN)Verificando saúde da API...$(NC)"
	curl -s http://localhost:8000/health | jq . || echo "API não está respondendo"
