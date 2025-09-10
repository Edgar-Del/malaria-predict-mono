# 🤖 Modelo ML - Dados Reais do Bié

## 🎯 Visão Geral

O módulo ML foi **completamente reorganizado** e **retreinado** usando dados reais da província do Bié (2020-2024). O modelo alcançou excelentes resultados com **99.1% de acurácia** nos dados históricos.

## 📊 Dataset Utilizado

- **Arquivo**: `data/raw/malaria_bie.csv`
- **Período**: 2020-2024 (5 anos)
- **Registros**: 450 observações
- **Municípios**: 9 municípios do Bié
- **Variáveis**: Ano, Semana, Município, Casos_Malaria, Temperatura_Media_C, Precipitacao_mm, Risco

## 🚀 Scripts Principais

### 1. `train_real_model.py`
**Treina o modelo com dados reais**
```bash
python train_real_model.py
```

**Funcionalidades:**
- Carrega dados reais do Bié
- Cria 17 features (temporais, climáticas, lag, médias móveis)
- Treina Random Forest Classifier
- Avalia performance (95.6% acurácia)
- Salva modelo e métricas

### 2. `test_real_model.py`
**Testa o modelo e gera predições**
```bash
python test_real_model.py
```

**Funcionalidades:**
- Testa acurácia nos dados históricos (99.1%)
- Gera predições para próximas 4 semanas
- Analisa performance por município
- Salva predições em CSV

### 3. `demo_model_usage.py`
**Demonstração interativa do modelo**
```bash
python demo_model_usage.py
```

**Funcionalidades:**
- Interface interativa para predições
- Exemplos de uso
- Interpretação de resultados
- Recomendações baseadas no risco

## 📈 Resultados Principais

### 🎯 Métricas de Performance
- **Acurácia no Teste**: 95.6%
- **Cross-Validation**: 96.7% (±2.4%)
- **Acurácia Histórica**: 99.1%

### 🏘️ Acurácia por Município
- **Camacupa, Cuito, Chinguar, Chitembo, Cuemba**: 100%
- **Andulo, Catabola, Cunhinga, Nharea**: 98%

### 🔍 Features Mais Importantes
1. **casos_temp_interaction** (40.2%)
2. **Precipitacao_mm** (15.9%)
3. **precip_norm** (14.7%)
4. **temp_precip_interaction** (9.9%)
5. **casos_ma3** (6.1%)

## 📁 Arquivos Gerados

### Modelos
- `models/malaria_risk_model_real.pkl` - Modelo treinado
- `models/label_encoder_risco.pkl` - Encoder para classes
- `models/label_encoder_municipio.pkl` - Encoder para municípios

### Dados Processados
- `data/processed/feature_importance_real.csv` - Importância das features
- `data/processed/model_metrics_real.csv` - Métricas do modelo
- `data/processed/predictions_next_weeks.csv` - Predições futuras

### Documentação
- `REAL_MODEL_REPORT.md` - Relatório detalhado
- `README_REAL_MODEL.md` - Este arquivo

## 🔮 Predições Atuais

### Próximas 4 Semanas (2024-11 a 2024-14)
- **Risco Alto**: Nharea, Cuemba (22.2%)
- **Risco Médio**: Demais municípios (77.8%)
- **Risco Baixo**: Nenhum (0%)

## 🎮 Como Usar

### 1. Treinar Modelo
```bash
cd ml
python train_real_model.py
```

### 2. Testar e Gerar Predições
```bash
python test_real_model.py
```

### 3. Demonstração Interativa
```bash
python demo_model_usage.py
```

### 4. Usar em Código
```python
import joblib

# Carregar modelo
model = joblib.load("models/malaria_risk_model_real.pkl")
le_risco = joblib.load("models/label_encoder_risco.pkl")
le_municipio = joblib.load("models/label_encoder_municipio.pkl")

# Fazer predição
prediction = model.predict(X)
risk = le_risco.inverse_transform(prediction)
```

## 📊 Interpretação dos Resultados

### Risco Alto (⚠️)
- **Confiança**: >90%
- **Ações**: Intensificar prevenção, distribuir mosquiteiros, monitoramento diário

### Risco Médio (⚡)
- **Confiança**: 70-90%
- **Ações**: Manter vigilância, preparar recursos

### Risco Baixo (✅)
- **Confiança**: >70%
- **Ações**: Medidas preventivas básicas, monitoramento contínuo

## 🔄 Atualizações Futuras

1. **Retreinamento**: Semanal/mensal com novos dados
2. **Validação**: Comparar predições com dados reais
3. **Melhorias**: Adicionar mais features (socioeconômicas, demográficas)
4. **Integração**: Conectar com dashboard e sistema de alertas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs detalhados
2. Execute `python test_real_model.py` para diagnóstico
3. Consulte `REAL_MODEL_REPORT.md` para métricas detalhadas

---
*Última atualização: 2025-09-08*
*Modelo: Random Forest Classifier*
*Dataset: malaria_bie.csv (2020-2024)*
