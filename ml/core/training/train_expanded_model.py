#!/usr/bin/env python3
"""
Script para treinar modelo ML com dataset expandido (18,720 registros)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from loguru import logger
from datetime import datetime

# Configurar logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="INFO"
)

# Caminhos
DATA_PATH = "../../../data/raw/malaria_bie_expanded.csv"
MODEL_PATH = "../models/"
PROCESSED_PATH = "../../../data/processed/"

def load_and_prepare_data():
    """Carrega e prepara os dados expandidos"""
    logger.info("📊 Carregando dataset expandido...")
    
    # Carregar dados
    df = pd.read_csv(DATA_PATH)
    logger.info(f"✅ Dataset carregado: {df.shape[0]:,} registros, {df.shape[1]} colunas")
    
    # Informações básicas
    logger.info(f"📅 Período: {df['Ano'].min()}-{df['Ano'].max()}")
    logger.info(f"🏘️ Municípios: {df['Municipio'].nunique()}")
    logger.info(f"📈 Total de casos: {df['Casos_Malaria'].sum():,}")
    logger.info(f"🎯 Classes de risco: {df['Risco'].value_counts().to_dict()}")
    
    return df

def create_features(df):
    """Cria features para o modelo ML"""
    logger.info("🔧 Criando features...")
    
    df_features = df.copy()
    
    # 1. Features temporais
    df_features['ano_semana'] = df_features['Ano'].astype(str) + '-' + df_features['Semana'].astype(str).str.zfill(2)
    
    # Features cíclicas para sazonalidade
    df_features['semana_sin'] = np.sin(2 * np.pi * df_features['Semana'] / 52)
    df_features['semana_cos'] = np.cos(2 * np.pi * df_features['Semana'] / 52)
    
    # Tendência temporal
    df_features['tendencia'] = (df_features['Ano'] - df_features['Ano'].min()) * 52 + df_features['Semana']
    
    # Estação do ano (aproximada)
    df_features['estacao'] = ((df_features['Semana'] - 1) // 13) + 1
    
    # 2. Features climáticas
    # Temperatura normalizada
    df_features['temp_norm'] = (df_features['Temperatura_Media_C'] - df_features['Temperatura_Media_C'].mean()) / df_features['Temperatura_Media_C'].std()
    
    # Precipitação normalizada
    df_features['precip_norm'] = (df_features['Precipitacao_mm'] - df_features['Precipitacao_mm'].mean()) / df_features['Precipitacao_mm'].std()
    
    # 3. Features de lag (casos da semana anterior)
    df_features = df_features.sort_values(['Municipio', 'Ano', 'Semana'])
    df_features['casos_lag1'] = df_features.groupby('Municipio')['Casos_Malaria'].shift(1)
    df_features['casos_lag2'] = df_features.groupby('Municipio')['Casos_Malaria'].shift(2)
    df_features['casos_lag3'] = df_features.groupby('Municipio')['Casos_Malaria'].shift(3)
    
    # 4. Features de média móvel
    df_features['casos_ma3'] = df_features.groupby('Municipio')['Casos_Malaria'].rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)
    df_features['casos_ma5'] = df_features.groupby('Municipio')['Casos_Malaria'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
    df_features['casos_ma10'] = df_features.groupby('Municipio')['Casos_Malaria'].rolling(window=10, min_periods=1).mean().reset_index(0, drop=True)
    
    # 5. Features de município (encoding)
    le_municipio = LabelEncoder()
    df_features['municipio_encoded'] = le_municipio.fit_transform(df_features['Municipio'])
    
    # 6. Features de interação
    df_features['temp_precip_interaction'] = df_features['Temperatura_Media_C'] * df_features['Precipitacao_mm']
    df_features['casos_temp_interaction'] = df_features['Casos_Malaria'] * df_features['Temperatura_Media_C']
    df_features['casos_precip_interaction'] = df_features['Casos_Malaria'] * df_features['Precipitacao_mm']
    
    # 7. Features estatísticas por município
    municipio_stats = df_features.groupby('Municipio')['Casos_Malaria'].agg(['mean', 'std', 'min', 'max']).reset_index()
    municipio_stats.columns = ['Municipio', 'municipio_casos_mean', 'municipio_casos_std', 'municipio_casos_min', 'municipio_casos_max']
    df_features = df_features.merge(municipio_stats, on='Municipio', how='left')
    
    # 8. Features relativas
    df_features['casos_vs_municipio_mean'] = df_features['Casos_Malaria'] / df_features['municipio_casos_mean']
    df_features['temp_vs_historical'] = df_features['Temperatura_Media_C'] / df_features.groupby('Semana')['Temperatura_Media_C'].transform('mean')
    df_features['precip_vs_historical'] = df_features['Precipitacao_mm'] / df_features.groupby('Semana')['Precipitacao_mm'].transform('mean')
    
    # Preencher NaNs dos lags
    df_features['casos_lag1'] = df_features['casos_lag1'].fillna(df_features['Casos_Malaria'].mean())
    df_features['casos_lag2'] = df_features['casos_lag2'].fillna(df_features['Casos_Malaria'].mean())
    df_features['casos_lag3'] = df_features['casos_lag3'].fillna(df_features['Casos_Malaria'].mean())
    
    logger.info(f"✅ Features criadas: {df_features.shape[1]} colunas")
    
    return df_features, le_municipio

def prepare_model_data(df_features):
    """Prepara dados para treinamento do modelo"""
    logger.info("🎯 Preparando dados para treinamento...")
    
    # Features para o modelo
    feature_columns = [
        'Ano', 'Semana', 'Temperatura_Media_C', 'Precipitacao_mm',
        'semana_sin', 'semana_cos', 'tendencia', 'estacao',
        'temp_norm', 'precip_norm', 'casos_lag1', 'casos_lag2', 'casos_lag3',
        'casos_ma3', 'casos_ma5', 'casos_ma10', 'municipio_encoded',
        'temp_precip_interaction', 'casos_temp_interaction', 'casos_precip_interaction',
        'municipio_casos_mean', 'municipio_casos_std', 'municipio_casos_min', 'municipio_casos_max',
        'casos_vs_municipio_mean', 'temp_vs_historical', 'precip_vs_historical'
    ]
    
    X = df_features[feature_columns]
    y = df_features['Risco']
    
    # Encoding da variável target
    le_risco = LabelEncoder()
    y_encoded = le_risco.fit_transform(y)
    
    logger.info(f"📊 Features: {X.shape[1]}")
    logger.info(f"🎯 Classes: {le_risco.classes_}")
    logger.info(f"📈 Distribuição: {np.bincount(y_encoded)}")
    
    return X, y_encoded, feature_columns, le_risco

def train_model(X, y):
    """Treina o modelo Random Forest"""
    logger.info("🤖 Treinando modelo Random Forest...")
    
    # Split dos dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"📊 Treino: {X_train.shape[0]:,} amostras")
    logger.info(f"📊 Teste: {X_test.shape[0]:,} amostras")
    
    # Modelo Random Forest otimizado para dataset maior
    model = RandomForestClassifier(
        n_estimators=200,  # Mais árvores para dataset maior
        max_depth=15,      # Profundidade maior
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',  # Otimização para datasets grandes
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # Balancear classes
    )
    
    # Treinamento
    logger.info("⏳ Iniciando treinamento...")
    model.fit(X_train, y_train)
    
    # Predições
    y_pred = model.predict(X_test)
    
    # Métricas
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"🎯 Acurácia: {accuracy:.3f}")
    
    # Cross-validation
    logger.info("⏳ Executando cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    logger.info(f"📊 CV Score (média): {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    return model, X_test, y_test, y_pred, accuracy, cv_scores

def evaluate_model(model, X_test, y_test, y_pred, le_risco, feature_columns):
    """Avalia o modelo e gera relatório detalhado"""
    logger.info("📊 Avaliando modelo...")
    
    # Relatório de classificação
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE CLASSIFICAÇÃO")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=le_risco.classes_))
    
    # Matriz de confusão
    print("\n" + "="*40)
    print("🔍 MATRIZ DE CONFUSÃO")
    print("="*40)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    print("\n" + "="*50)
    print("🔍 TOP 15 FEATURES MAIS IMPORTANTES")
    print("="*50)
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for i, (_, row) in enumerate(importance_df.head(15).iterrows()):
        print(f"{i+1:2d}. {row['feature']:30s}: {row['importance']:.3f}")
    
    return importance_df

def save_model_and_data(model, le_risco, le_municipio, importance_df, accuracy, cv_scores):
    """Salva modelo e dados processados"""
    logger.info("💾 Salvando modelo e dados...")
    
    # Criar diretórios
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    
    # Salvar modelo
    model_file = os.path.join(MODEL_PATH, "malaria_risk_model_expanded.pkl")
    joblib.dump(model, model_file)
    logger.info(f"✅ Modelo salvo: {model_file}")
    
    # Salvar encoders
    joblib.dump(le_risco, os.path.join(MODEL_PATH, "label_encoder_risco_expanded.pkl"))
    joblib.dump(le_municipio, os.path.join(MODEL_PATH, "label_encoder_municipio_expanded.pkl"))
    
    # Salvar feature importance
    importance_df.to_csv(os.path.join(PROCESSED_PATH, "feature_importance_expanded.csv"), index=False)
    
    # Salvar métricas
    metrics = {
        'accuracy': accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'timestamp': datetime.now().isoformat(),
        'model_type': 'RandomForestClassifier',
        'dataset': 'malaria_bie_expanded.csv',
        'records': 18720,
        'features': len(importance_df)
    }
    
    pd.DataFrame([metrics]).to_csv(os.path.join(PROCESSED_PATH, "model_metrics_expanded.csv"), index=False)
    
    logger.info("✅ Todos os arquivos salvos!")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando treinamento com dataset expandido...")
    
    try:
        # 1. Carregar dados
        df = load_and_prepare_data()
        
        # 2. Criar features
        df_features, le_municipio = create_features(df)
        
        # 3. Preparar dados para modelo
        X, y, feature_columns, le_risco = prepare_model_data(df_features)
        
        # 4. Treinar modelo
        model, X_test, y_test, y_pred, accuracy, cv_scores = train_model(X, y)
        
        # 5. Avaliar modelo
        importance_df = evaluate_model(model, X_test, y_test, y_pred, le_risco, feature_columns)
        
        # 6. Salvar modelo e dados
        save_model_and_data(model, le_risco, le_municipio, importance_df, accuracy, cv_scores)
        
        logger.info("🎉 Treinamento concluído com sucesso!")
        
        # Resumo final
        print("\n" + "="*60)
        print("🎉 RESUMO DO TREINAMENTO - DATASET EXPANDIDO")
        print("="*60)
        print(f"📊 Dataset: {df.shape[0]:,} registros, {df.shape[1]} colunas")
        print(f"🏘️ Municípios: {df['Municipio'].nunique()}")
        print(f"📅 Período: {df['Ano'].min()}-{df['Ano'].max()}")
        print(f"🎯 Acurácia: {accuracy:.3f}")
        print(f"📊 CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        print(f"🔍 Features: {len(feature_columns)}")
        print(f"💾 Modelo salvo em: {MODEL_PATH}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante treinamento: {e}")
        raise

if __name__ == "__main__":
    main()
