# ML Makefile - Sistema de Previsão de Malária - Bié

.PHONY: help install dev train predict evaluate visualize clean

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)ML - Sistema de Previsão de Malária$(NC)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências Python
	@echo "$(GREEN)Instalando dependências do ML...$(NC)"
	pip install -e .

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(GREEN)Instalando dependências de desenvolvimento...$(NC)"
	pip install -e ".[dev]"

dev: ## Inicia Jupyter notebook
	@echo "$(GREEN)Iniciando Jupyter notebook...$(NC)"
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

train: ## Treina o modelo
	@echo "$(GREEN)Treinando modelo...$(NC)"
	python -m training.train_model

predict: ## Executa predições
	@echo "$(GREEN)Executando predições...$(NC)"
	python -m serving.predict

evaluate: ## Avalia o modelo
	@echo "$(GREEN)Avaliando modelo...$(NC)"
	python -m training.evaluate_model

visualize: ## Gera visualizações
	@echo "$(GREEN)Gerando visualizações...$(NC)"
	python -m data.visualize

preprocess: ## Preprocessa dados
	@echo "$(GREEN)Preprocessando dados...$(NC)"
	python -m data.preprocess

feature-engineering: ## Executa engenharia de features
	@echo "$(GREEN)Executando engenharia de features...$(NC)"
	python -m features.engineer

hyperparameter-tuning: ## Executa otimização de hiperparâmetros
	@echo "$(GREEN)Otimizando hiperparâmetros...$(NC)"
	python -m training.hyperparameter_tuning

model-validation: ## Valida o modelo
	@echo "$(GREEN)Validando modelo...$(NC)"
	python -m training.validate_model

mlflow-ui: ## Inicia MLflow UI
	@echo "$(GREEN)Iniciando MLflow UI...$(NC)"
	mlflow ui --host 0.0.0.0 --port 5000

experiment: ## Executa experimento completo
	@echo "$(GREEN)Executando experimento completo...$(NC)"
	python -m training.run_experiment

test: ## Executa testes
	@echo "$(GREEN)Executando testes do ML...$(NC)"
	pytest tests/ -v

lint: ## Executa linter
	@echo "$(GREEN)Executando linter...$(NC)"
	flake8 features/ models/ training/ serving/ data/

format: ## Formata código
	@echo "$(GREEN)Formatando código...$(NC)"
	black features/ models/ training/ serving/ data/ tests/
	isort features/ models/ training/ serving/ data/ tests/

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
	rm -rf .coverage htmlcov/ dist/ build/ mlruns/
	rm -rf data/processed/*.csv data/processed/*.parquet
	rm -rf models/*.joblib models/*.pkl models/*.h5

data-check: ## Verifica qualidade dos dados
	@echo "$(GREEN)Verificando qualidade dos dados...$(NC)"
	python -m data.quality_check

model-info: ## Mostra informações do modelo
	@echo "$(GREEN)Informações do modelo...$(NC)"
	python -m models.model_info

deploy-model: ## Deploy do modelo
	@echo "$(GREEN)Fazendo deploy do modelo...$(NC)"
	python -m serving.deploy

monitor-model: ## Monitora performance do modelo
	@echo "$(GREEN)Monitorando modelo...$(NC)"
	python -m serving.monitor

pipeline: ## Executa pipeline completo
	@echo "$(GREEN)Executando pipeline completo...$(NC)"
	$(MAKE) preprocess
	$(MAKE) feature-engineering
	$(MAKE) train
	$(MAKE) evaluate
	$(MAKE) visualize
