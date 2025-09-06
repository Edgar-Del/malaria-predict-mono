# ML - Sistema de Previsão de Malária - Bié

Módulo de Machine Learning para previsão de risco de malária utilizando scikit-learn e MLflow.

## 🏗️ Arquitetura

```
ml/
├── data/                  # Processamento de dados
│   ├── preprocess.py     # Pré-processamento
│   ├── visualize.py      # Visualizações
│   └── quality_check.py  # Verificação de qualidade
├── features/             # Engenharia de features
│   └── engineer.py       # Criação de features
├── models/               # Modelos de ML
│   ├── trainer.py        # Treinamento
│   ├── predictor.py      # Predição
│   └── evaluator.py      # Avaliação
├── training/             # Scripts de treinamento
│   ├── train_model.py    # Treinamento principal
│   ├── hyperparameter_tuning.py # Otimização
│   └── validate_model.py # Validação
├── serving/              # Servir modelos
│   ├── predict.py        # Predições
│   ├── deploy.py         # Deploy
│   └── monitor.py        # Monitoramento
└── requirements.txt      # Dependências Python
```

## 🚀 Instalação e Execução

### Desenvolvimento Local

```bash
# Instalar dependências
make install

# Executar pipeline completo
make pipeline

# Treinar modelo
make train

# Executar testes
make test
```

### Docker

```bash
# Construir imagem
docker build -t malaria-ml .

# Executar container
docker run -p 5000:5000 malaria-ml
```

## 🤖 Modelos de ML

### Algoritmos Implementados

- **Random Forest**: Classificador principal
- **Gradient Boosting**: Alternativa robusta
- **SVM**: Suporte para dados lineares
- **Logistic Regression**: Baseline simples

### Pipeline de ML

1. **Pré-processamento**: Limpeza e validação
2. **Feature Engineering**: Criação de atributos
3. **Treinamento**: Otimização de hiperparâmetros
4. **Validação**: Cross-validation estratificada
5. **Deploy**: Servir modelo em produção

## 📊 Engenharia de Features

### Features Temporais
- **Lags**: Valores anteriores (1-4 semanas)
- **Médias Móveis**: Janelas de 2 e 4 semanas
- **Sazonalidade**: Componentes cíclicos

### Features Climáticas
- **Precipitação**: Chuva acumulada e média
- **Temperatura**: Média, mínima, máxima
- **Umidade**: Relativa e absoluta
- **Índices**: Conforto térmico, amplitude

### Features Epidemiológicas
- **Taxa de Crescimento**: Variação de casos
- **Aceleração**: Segunda derivada
- **Percentis**: Classificação histórica

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Banco de Dados
DATABASE_URL=postgresql://malaria_user:malaria_pass@localhost:5432/malaria_bie

# Modelo
MODEL_PATH=models/malaria_model.joblib
RANDOM_STATE=42

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=malaria_prediction
```

### Configuração MLflow

```python
# mlflow_config.py
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("malaria_prediction")
```

## 🧪 Experimentos

### Executar Experimento

```bash
# Experimento completo
make experiment

# Hiperparâmetros
make hyperparameter-tuning

# Validação
make model-validation
```

### MLflow UI

```bash
# Iniciar MLflow UI
make mlflow-ui

# Acessar: http://localhost:5000
```

## 📈 Avaliação de Modelos

### Métricas

- **Accuracy**: Precisão geral
- **Precision**: Precisão por classe
- **Recall**: Sensibilidade por classe
- **F1-Score**: Média harmônica
- **Confusion Matrix**: Matriz de confusão

### Validação

- **Cross-Validation**: 5-fold estratificado
- **Time Series Split**: Validação temporal
- **Holdout**: Teste final
- **Bootstrap**: Estimativa de confiança

## 🔧 Desenvolvimento

### Estrutura de Código

```python
# Exemplo de treinamento
from models.trainer import ModelTrainer
from data.preprocess import DataPreprocessor

# Pré-processar dados
preprocessor = DataPreprocessor()
X, y = preprocessor.fit_transform(data)

# Treinar modelo
trainer = ModelTrainer()
model = trainer.train(X, y)

# Avaliar
metrics = trainer.evaluate(model, X_test, y_test)
```

### Feature Engineering

```python
# Exemplo de feature engineering
from features.engineer import FeatureEngineer

engineer = FeatureEngineer()

# Criar features temporais
df_lags = engineer.create_lag_features(df, 'casos', [1, 2, 3, 4])

# Criar features sazonais
df_seasonal = engineer.create_seasonal_features(df_lags)

# Criar features climáticas
df_climate = engineer.create_climate_features(df_seasonal)
```

## 📊 Visualizações

### Gráficos de Análise

- **Distribuição**: Histogramas de features
- **Correlação**: Matriz de correlação
- **Importância**: Features mais importantes
- **Performance**: Curvas de aprendizado

### Métricas de Modelo

- **ROC Curves**: Curvas ROC por classe
- **Precision-Recall**: Curvas PR
- **Confusion Matrix**: Matriz de confusão
- **Feature Importance**: Importância das features

## 🚀 Deploy

### Modelo em Produção

```bash
# Deploy do modelo
make deploy-model

# Monitorar performance
make monitor-model
```

### Servir Predições

```python
# Exemplo de predição
from serving.predict import ModelPredictor

predictor = ModelPredictor()
prediction = predictor.predict(municipio="Kuito", semana="2024-01")
```

## 📊 Monitoramento

### Métricas de Produção

- **Drift Detection**: Detecção de drift
- **Performance**: Acurácia em tempo real
- **Data Quality**: Qualidade dos dados
- **Model Health**: Saúde do modelo

### Alertas

- **Accuracy Drop**: Queda de performance
- **Data Drift**: Mudança nos dados
- **Model Staleness**: Modelo desatualizado
- **System Errors**: Erros do sistema

## 🔧 Desenvolvimento

### Estrutura de Testes

```python
# Exemplo de teste
import pytest
from models.trainer import ModelTrainer

def test_model_training():
    trainer = ModelTrainer()
    X, y = create_sample_data()
    model = trainer.train(X, y)
    assert model is not None
    assert trainer.evaluate(model, X, y)['accuracy'] > 0.8
```

### Padrões de Código

- **Python**: PEP 8, Black, Flake8
- **ML**: Scikit-learn best practices
- **Testing**: Pytest com fixtures
- **Documentation**: Docstrings completas

## 📈 Performance

### Otimizações

- **Feature Selection**: Seleção de features
- **Hyperparameter Tuning**: Otimização de parâmetros
- **Cross-Validation**: Validação robusta
- **Ensemble Methods**: Métodos ensemble

### Escalabilidade

- **Batch Processing**: Processamento em lote
- **Parallel Training**: Treinamento paralelo
- **Model Caching**: Cache de modelos
- **Incremental Learning**: Aprendizado incremental

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
