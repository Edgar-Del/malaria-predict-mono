# 🤖 Módulo ML - Sistema de Previsão de Malária

## 📁 Estrutura do Projeto

```
ml/
├── core/                           # Código principal do ML
│   ├── models/                     # Modelos treinados
│   │   ├── malaria_risk_model_expanded.pkl
│   │   ├── label_encoder_risco_expanded.pkl
│   │   └── label_encoder_municipio_expanded.pkl
│   ├── features/                   # Engenharia de features
│   │   └── feature_engineering.py
│   ├── training/                   # Scripts de treinamento
│   │   └── train_expanded_model.py
│   ├── data/                       # Fontes de dados
│   │   └── data_sources/
│   │       ├── fetch_climate_open_meteo.py
│   │       └── reports/
│   │           ├── download_reports.py
│   │           ├── parse_reports.py
│   │           └── urls.txt
│   └── requirements.txt            # Dependências
├── scripts/                        # Scripts utilitários
│   ├── compare_models.py           # Comparação de modelos
│   ├── demo_model_usage.py         # Demonstração interativa
│   ├── generate_large_dataset.py   # Geração de dataset expandido
│   ├── test_real_model.py          # Testes do modelo
│   └── ...
├── docs/                           # Documentação
│   ├── EXPANDED_DATASET_REPORT.md  # Relatório do dataset expandido
│   ├── README_REAL_MODEL.md        # Guia do modelo real
│   └── REAL_MODEL_REPORT.md        # Relatório do modelo real
├── data/                           # Dados processados (link simbólico)
└── README.md                       # Este arquivo
```

## 🚀 Uso Rápido

### 1. Treinar Modelo
```bash
cd core/training
python train_expanded_model.py
```

### 2. Comparar Modelos
```bash
cd scripts
python compare_models.py
```

### 3. Demonstração Interativa
```bash
cd scripts
python demo_model_usage.py
```

### 4. Gerar Dataset Expandido
```bash
cd scripts
python generate_large_dataset.py
```

### 5. Testar Modelo
```bash
cd scripts
python test_real_model.py
```

## 📊 Modelo Atual

- **Dataset**: 18,720 registros (2010-2024)
- **Municípios**: 24 municípios do Bié
- **Acurácia**: 97.9%
- **Features**: 27 variáveis avançadas
- **Algoritmo**: Random Forest Classifier

## 🔍 Features Mais Importantes

1. **casos_vs_municipio_mean** (27.8%) - Comparação relativa
2. **casos_temp_interaction** (21.1%) - Interação clima-casos
3. **casos_ma3** (9.7%) - Média móvel de 3 semanas
4. **casos_ma5** (7.2%) - Média móvel de 5 semanas
5. **casos_lag1** (4.5%) - Casos da semana anterior

## 📈 Performance

| Métrica | Valor |
|---------|-------|
| **Acurácia** | 97.9% |
| **CV Score** | 95.0% |
| **Precision (Alto)** | 96% |
| **Recall (Alto)** | 99% |
| **F1-Score (Alto)** | 97% |

## 🎯 Classes de Risco

- **Alto**: 1,092 registros (5.8%)
- **Médio**: 6,311 registros (33.7%)
- **Baixo**: 11,317 registros (60.5%)

## 📚 Documentação

- [Relatório do Dataset Expandido](docs/EXPANDED_DATASET_REPORT.md)
- [Guia do Modelo Real](docs/README_REAL_MODEL.md)
- [Relatório do Modelo Real](docs/REAL_MODEL_REPORT.md)

## 🔧 Instalação

```bash
# Instalar dependências
pip install -r core/requirements.txt

# Ativar ambiente virtual (recomendado)
source .venv-ml/bin/activate
```

## 🚀 Próximos Passos

1. **Integração**: Conectar com dashboard
2. **Alertas**: Sistema de notificações automáticas
3. **Retreinamento**: Atualização automática semanal
4. **Expansão**: Adicionar mais features (socioeconômicas)

---
*Última atualização: 2025-09-08*
*Versão: 2.0 (Dataset Expandido)*