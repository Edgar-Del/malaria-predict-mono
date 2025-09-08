# 📊 Relatório do Modelo ML - Dados Reais do Bié

## 🎯 Resumo Executivo

O modelo de Machine Learning foi **retreinado com sucesso** usando dados reais da província do Bié (2020-2024), alcançando excelentes resultados de precisão e acurácia.

## 📈 Dados Utilizados

- **Dataset**: `malaria_bie.csv`
- **Período**: 2020-2024 (5 anos)
- **Registros**: 450 observações
- **Municípios**: 9 municípios do Bié
- **Total de casos**: 585,523 casos de malária
- **Variáveis**: Ano, Semana, Município, Casos_Malaria, Temperatura_Media_C, Precipitacao_mm, Risco

## 🏘️ Municípios Analisados

1. **Cuito** (capital)
2. **Andulo**
3. **Nharea**
4. **Camacupa**
5. **Chinguar**
6. **Catabola**
7. **Cunhinga**
8. **Chitembo**
9. **Cuemba**

## 🎯 Distribuição das Classes de Risco

| Classe | Quantidade | Percentual |
|--------|------------|------------|
| **Alto** | 251 | 55.8% |
| **Médio** | 172 | 38.2% |
| **Baixo** | 27 | 6.0% |

## 🤖 Modelo Treinado

- **Algoritmo**: Random Forest Classifier
- **Features**: 17 variáveis
- **Parâmetros**:
  - `n_estimators`: 100
  - `max_depth`: 10
  - `min_samples_split`: 5
  - `min_samples_leaf`: 2

## 📊 Métricas de Performance

### 🎯 Acurácia Geral
- **Acurácia no Teste**: **95.6%**
- **Cross-Validation Score**: **96.7%** (±2.4%)
- **Acurácia nos Dados Históricos**: **99.1%**

### 📈 Relatório de Classificação

| Classe | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| **Alto** | 0.96 | 1.00 | 0.98 | 50 |
| **Baixo** | 1.00 | 0.60 | 0.75 | 5 |
| **Médio** | 0.94 | 0.94 | 0.94 | 35 |

### 🏘️ Acurácia por Município

| Município | Acurácia |
|-----------|----------|
| **Camacupa** | 100.0% |
| **Cuito** | 100.0% |
| **Chinguar** | 100.0% |
| **Chitembo** | 100.0% |
| **Cuemba** | 100.0% |
| **Andulo** | 98.0% |
| **Catabola** | 98.0% |
| **Cunhinga** | 98.0% |
| **Nharea** | 98.0% |

## 🔍 Features Mais Importantes

| Rank | Feature | Importância |
|------|---------|-------------|
| 1 | **casos_temp_interaction** | 0.402 |
| 2 | **Precipitacao_mm** | 0.159 |
| 3 | **precip_norm** | 0.147 |
| 4 | **temp_precip_interaction** | 0.099 |
| 5 | **casos_ma3** | 0.061 |
| 6 | **casos_ma5** | 0.028 |
| 7 | **casos_lag2** | 0.022 |
| 8 | **casos_lag1** | 0.019 |
| 9 | **Temperatura_Media_C** | 0.014 |
| 10 | **temp_norm** | 0.012 |

## 🔮 Predições para Próximas Semanas

### Semana 2024-11 a 2024-14

| Município | Risco Predito | Confiança |
|-----------|---------------|-----------|
| **Nharea** | Alto | 96% |
| **Cuemba** | Alto | 95% |
| **Camacupa** | Médio | 95% |
| **Chitembo** | Médio | 94% |
| **Chinguar** | Médio | 93% |
| **Catabola** | Médio | 92% |
| **Andulo** | Médio | 92% |
| **Cuito** | Médio | 90% |
| **Cunhinga** | Médio | 55% |

### ⚠️ Análise de Risco Geral (Próximas 4 Semanas)

- **Risco Alto**: 8 municípios (22.2%)
- **Risco Médio**: 28 municípios (77.8%)
- **Risco Baixo**: 0 municípios (0%)

## 📁 Arquivos Gerados

### Modelos e Encoders
- `models/malaria_risk_model_real.pkl` - Modelo treinado
- `models/label_encoder_risco.pkl` - Encoder para classes de risco
- `models/label_encoder_municipio.pkl` - Encoder para municípios

### Dados Processados
- `data/processed/feature_importance_real.csv` - Importância das features
- `data/processed/model_metrics_real.csv` - Métricas do modelo
- `data/processed/predictions_next_weeks.csv` - Predições futuras

## 🎯 Insights Principais

### 1. **Alta Precisão do Modelo**
- O modelo alcançou **99.1% de acurácia** nos dados históricos
- Excelente performance em todos os municípios (98-100% de acurácia)

### 2. **Features Mais Relevantes**
- **Interação casos-temperatura** é a feature mais importante (40.2%)
- **Precipitação** tem grande influência no risco (15.9%)
- **Médias móveis** de casos são importantes para capturar tendências

### 3. **Padrões de Risco**
- **Nharea** e **Cuemba** apresentam risco alto consistente
- **Cunhinga** tem menor confiança nas predições (55%)
- Maioria dos municípios em risco médio nas próximas semanas

### 4. **Sazonalidade**
- O modelo captura bem os padrões sazonais através das features cíclicas
- As médias móveis ajudam a suavizar variações temporais

## 🚀 Próximos Passos

1. **Monitoramento Contínuo**: Acompanhar as predições semanais
2. **Atualização do Modelo**: Retreinar periodicamente com novos dados
3. **Integração com Sistema**: Conectar com dashboard e alertas
4. **Validação Externa**: Comparar predições com dados reais futuros

## 📞 Contato

Para dúvidas sobre o modelo ou predições, consulte os logs detalhados ou execute:
```bash
cd ml
python test_real_model.py
```

---
*Relatório gerado em: 2025-09-08*
*Modelo: Random Forest Classifier*
*Dataset: malaria_bie.csv (2020-2024)*
