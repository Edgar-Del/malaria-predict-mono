FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código ML
COPY . .

# Criar diretórios necessários
RUN mkdir -p models data/raw data/processed logs

# Expor porta (para MLflow UI)
EXPOSE 5000

# Comando padrão
CMD ["python", "-m", "training.train_model"]
