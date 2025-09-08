#!/usr/bin/env python3
"""
Script para testar o modelo ML treinado com dados reais
"""

import pandas as pd
import numpy as np
import joblib
import os
from loguru import logger
from datetime import datetime, timedelta

# Configurar logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="INFO"
)

# Caminhos
MODEL_PATH = "models/"
DATA_PATH = "../data/raw/malaria_bie.csv"

def load_model_and_encoders():
    """Carrega modelo e encoders salvos"""
    logger.info("📦 Carregando modelo e encoders...")
    
    model = joblib.load(os.path.join(MODEL_PATH, "malaria_risk_model_real.pkl"))
    le_risco = joblib.load(os.path.join(MODEL_PATH, "label_encoder_risco.pkl"))
    le_municipio = joblib.load(os.path.join(MODEL_PATH, "label_encoder_municipio.pkl"))
    
    logger.info("✅ Modelo e encoders carregados!")
    return model, le_risco, le_municipio

def create_features_for_prediction(df, le_municipio):
    """Cria features para predição (mesma lógica do treinamento)"""
    df_features = df.copy()
    
    # Features temporais
    df_features['ano_semana'] = df_features['Ano'].astype(str) + '-' + df_features['Semana'].astype(str).str.zfill(2)
    df_features['semana_sin'] = np.sin(2 * np.pi * df_features['Semana'] / 52)
    df_features['semana_cos'] = np.cos(2 * np.pi * df_features['Semana'] / 52)
    df_features['tendencia'] = (df_features['Ano'] - df_features['Ano'].min()) * 52 + df_features['Semana']
    df_features['estacao'] = ((df_features['Semana'] - 1) // 13) + 1
    
    # Features climáticas
    df_features['temp_norm'] = (df_features['Temperatura_Media_C'] - df_features['Temperatura_Media_C'].mean()) / df_features['Temperatura_Media_C'].std()
    df_features['precip_norm'] = (df_features['Precipitacao_mm'] - df_features['Precipitacao_mm'].mean()) / df_features['Precipitacao_mm'].std()
    
    # Features de lag
    df_features = df_features.sort_values(['Municipio', 'Ano', 'Semana'])
    df_features['casos_lag1'] = df_features.groupby('Municipio')['Casos_Malaria'].shift(1)
    df_features['casos_lag2'] = df_features.groupby('Municipio')['Casos_Malaria'].shift(2)
    
    # Features de média móvel
    df_features['casos_ma3'] = df_features.groupby('Municipio')['Casos_Malaria'].rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)
    df_features['casos_ma5'] = df_features.groupby('Municipio')['Casos_Malaria'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
    
    # Encoding de município
    df_features['municipio_encoded'] = le_municipio.transform(df_features['Municipio'])
    
    # Features de interação
    df_features['temp_precip_interaction'] = df_features['Temperatura_Media_C'] * df_features['Precipitacao_mm']
    df_features['casos_temp_interaction'] = df_features['Casos_Malaria'] * df_features['Temperatura_Media_C']
    
    # Preencher NaNs
    df_features['casos_lag1'] = df_features['casos_lag1'].fillna(df_features['Casos_Malaria'].mean())
    df_features['casos_lag2'] = df_features['casos_lag2'].fillna(df_features['Casos_Malaria'].mean())
    
    return df_features

def predict_risk(model, df_features, le_risco):
    """Faz predições de risco"""
    feature_columns = [
        'Ano', 'Semana', 'Temperatura_Media_C', 'Precipitacao_mm',
        'semana_sin', 'semana_cos', 'tendencia', 'estacao',
        'temp_norm', 'precip_norm', 'casos_lag1', 'casos_lag2',
        'casos_ma3', 'casos_ma5', 'municipio_encoded',
        'temp_precip_interaction', 'casos_temp_interaction'
    ]
    
    X = df_features[feature_columns]
    
    # Predições
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    # Decodificar predições
    risk_predictions = le_risco.inverse_transform(predictions)
    
    # Adicionar ao DataFrame
    df_features['Risco_Predito'] = risk_predictions
    df_features['Confianca_Alto'] = probabilities[:, 0]  # Alto
    df_features['Confianca_Baixo'] = probabilities[:, 1]  # Baixo
    df_features['Confianca_Medio'] = probabilities[:, 2]  # Médio
    
    return df_features

def test_model_accuracy():
    """Testa a acurácia do modelo nos dados históricos"""
    logger.info("🧪 Testando acurácia do modelo...")
    
    # Carregar dados
    df = pd.read_csv(DATA_PATH)
    
    # Carregar modelo
    model, le_risco, le_municipio = load_model_and_encoders()
    
    # Criar features
    df_features = create_features_for_prediction(df, le_municipio)
    
    # Fazer predições
    df_with_predictions = predict_risk(model, df_features, le_risco)
    
    # Calcular acurácia
    accuracy = (df_with_predictions['Risco'] == df_with_predictions['Risco_Predito']).mean()
    
    logger.info(f"🎯 Acurácia nos dados históricos: {accuracy:.3f}")
    
    # Análise por município
    print("\n" + "="*60)
    print("📊 ACURÁCIA POR MUNICÍPIO")
    print("="*60)
    accuracy_by_municipio = df_with_predictions.groupby('Municipio').apply(
        lambda x: (x['Risco'] == x['Risco_Predito']).mean()
    ).sort_values(ascending=False)
    
    for municipio, acc in accuracy_by_municipio.items():
        print(f"{municipio:12s}: {acc:.3f}")
    
    return df_with_predictions, accuracy

def generate_predictions_for_next_weeks():
    """Gera predições para as próximas semanas"""
    logger.info("🔮 Gerando predições para próximas semanas...")
    
    # Carregar dados históricos
    df = pd.read_csv(DATA_PATH)
    
    # Carregar modelo
    model, le_risco, le_municipio = load_model_and_encoders()
    
    # Última semana dos dados
    last_year = df['Ano'].max()
    last_week = df[df['Ano'] == last_year]['Semana'].max()
    
    logger.info(f"📅 Última semana nos dados: {last_year}-{last_week}")
    
    # Gerar predições para próximas 4 semanas
    predictions_list = []
    
    for week_offset in range(1, 5):
        target_week = last_week + week_offset
        target_year = last_year
        
        # Ajustar ano se necessário
        if target_week > 52:
            target_week = target_week - 52
            target_year += 1
        
        logger.info(f"🔮 Predizendo semana {target_year}-{target_week}...")
        
        # Para cada município
        for municipio in df['Municipio'].unique():
            # Dados históricos do município
            municipio_data = df[df['Municipio'] == municipio].copy()
            
            # Últimos dados conhecidos
            last_data = municipio_data.iloc[-1]
            
            # Criar dados para predição (usando valores médios históricos)
            pred_data = {
                'Ano': target_year,
                'Semana': target_week,
                'Municipio': municipio,
                'Casos_Malaria': last_data['Casos_Malaria'],  # Usar último valor conhecido
                'Temperatura_Media_C': municipio_data['Temperatura_Media_C'].mean(),
                'Precipitacao_mm': municipio_data['Precipitacao_mm'].mean(),
                'Risco': 'Médio'  # Placeholder
            }
            
            # Criar DataFrame temporário
            temp_df = pd.DataFrame([pred_data])
            
            # Criar features
            temp_features = create_features_for_prediction(temp_df, le_municipio)
            
            # Fazer predição
            temp_with_pred = predict_risk(model, temp_features, le_risco)
            
            # Adicionar à lista
            predictions_list.append({
                'Ano': target_year,
                'Semana': target_week,
                'Municipio': municipio,
                'Risco_Predito': temp_with_pred['Risco_Predito'].iloc[0],
                'Confianca_Alto': temp_with_pred['Confianca_Alto'].iloc[0],
                'Confianca_Baixo': temp_with_pred['Confianca_Baixo'].iloc[0],
                'Confianca_Medio': temp_with_pred['Confianca_Medio'].iloc[0],
                'Temperatura_Media_C': pred_data['Temperatura_Media_C'],
                'Precipitacao_mm': pred_data['Precipitacao_mm']
            })
    
    # Criar DataFrame de predições
    predictions_df = pd.DataFrame(predictions_list)
    
    # Salvar predições
    predictions_df.to_csv("../data/processed/predictions_next_weeks.csv", index=False)
    
    logger.info("✅ Predições salvas em: ../data/processed/predictions_next_weeks.csv")
    
    return predictions_df

def main():
    """Função principal"""
    logger.info("🧪 Iniciando testes do modelo...")
    
    try:
        # 1. Testar acurácia
        df_with_predictions, accuracy = test_model_accuracy()
        
        # 2. Gerar predições futuras
        predictions_df = generate_predictions_for_next_weeks()
        
        # 3. Resumo das predições
        print("\n" + "="*60)
        print("🔮 PREDIÇÕES PARA PRÓXIMAS SEMANAS")
        print("="*60)
        
        for week in predictions_df['Semana'].unique():
            week_data = predictions_df[predictions_df['Semana'] == week]
            print(f"\n📅 Semana {week_data['Ano'].iloc[0]}-{week}:")
            
            for _, row in week_data.iterrows():
                confianca = max(row['Confianca_Alto'], row['Confianca_Baixo'], row['Confianca_Medio'])
                print(f"  {row['Municipio']:12s}: {row['Risco_Predito']:6s} (confiança: {confianca:.2f})")
        
        # 4. Análise de risco geral
        print("\n" + "="*50)
        print("⚠️ ANÁLISE DE RISCO GERAL")
        print("="*50)
        
        risk_counts = predictions_df['Risco_Predito'].value_counts()
        total_predictions = len(predictions_df)
        
        for risk, count in risk_counts.items():
            percentage = (count / total_predictions) * 100
            print(f"{risk:6s}: {count:2d} municípios ({percentage:5.1f}%)")
        
        logger.info("🎉 Testes concluídos com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante testes: {e}")
        raise

if __name__ == "__main__":
    main()
