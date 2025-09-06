# Frontend Makefile - Sistema de Previsão de Malária - Bié

.PHONY: help install dev build start test lint format clean

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)Frontend - Sistema de Previsão de Malária$(NC)"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências Node.js
	@echo "$(GREEN)Instalando dependências do frontend...$(NC)"
	npm install

dev: ## Executa o dashboard em modo desenvolvimento
	@echo "$(GREEN)Iniciando dashboard em modo desenvolvimento...$(NC)"
	npm run dev

build: ## Constrói o projeto para produção
	@echo "$(GREEN)Construindo projeto para produção...$(NC)"
	npm run build

start: ## Executa o dashboard em modo produção
	@echo "$(GREEN)Iniciando dashboard em modo produção...$(NC)"
	npm start

test: ## Executa testes
	@echo "$(GREEN)Executando testes do frontend...$(NC)"
	npm run test

lint: ## Executa linter
	@echo "$(GREEN)Executando linter...$(NC)"
	npm run lint

format: ## Formata código
	@echo "$(GREEN)Formatando código...$(NC)"
	npm run format

type-check: ## Verifica tipos TypeScript
	@echo "$(GREEN)Verificando tipos...$(NC)"
	npm run type-check

check: ## Executa verificações (lint + type-check + test)
	@echo "$(GREEN)Executando verificações...$(NC)"
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

clean: ## Limpa arquivos temporários
	@echo "$(GREEN)Limpando arquivos temporários...$(NC)"
	rm -rf .next/ out/ dist/ node_modules/.cache
	npm run clean 2>/dev/null || true

analyze: ## Analisa bundle
	@echo "$(GREEN)Analisando bundle...$(NC)"
	npm run build
	npm run analyze

audit: ## Audita dependências
	@echo "$(GREEN)Auditando dependências...$(NC)"
	npm audit

audit-fix: ## Corrige vulnerabilidades
	@echo "$(GREEN)Corrigindo vulnerabilidades...$(NC)"
	npm audit fix

update: ## Atualiza dependências
	@echo "$(GREEN)Atualizando dependências...$(NC)"
	npm update

outdated: ## Mostra dependências desatualizadas
	@echo "$(GREEN)Verificando dependências desatualizadas...$(NC)"
	npm outdated

dev-full: ## Executa sistema completo em modo desenvolvimento
	@echo "$(GREEN)Iniciando sistema completo...$(NC)"
	@echo "Execute em terminais separados:"
	@echo "  Terminal 1: make -C ../backend dev"
	@echo "  Terminal 2: make dev"
	@echo "  Terminal 3: docker-compose up postgres"

status: ## Verifica status do frontend
	@echo "$(GREEN)Verificando status do frontend...$(NC)"
	@if curl -s http://localhost:3000 > /dev/null; then \
		echo "✅ Dashboard está rodando em http://localhost:3000"; \
	else \
		echo "❌ Dashboard não está rodando"; \
	fi
