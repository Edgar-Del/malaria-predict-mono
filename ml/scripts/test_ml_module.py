#!/usr/bin/env python3
"""
Script para testar o módulo ML e apresentar métricas.
"""

import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime

# Adicionar o diretório ml ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ml_module():
    """Testa o módulo ML completo."""
    
    print("🤖 Testando Módulo de Machine Learning")
    print("=" * 50)
    
    try:
        # 1. Carregar dados
        print("\n📊 1. Carregando dados...")
        data_path = '../data/processed/malaria_data_sample.csv'
        
        if not os.path.exists(data_path):
            print("❌ Dados não encontrados. Execute primeiro generate_sample_data.py")
            return False
            
        df = pd.read_csv(data_path)
        df['data'] = pd.to_datetime(df['data'])
        print(f"✅ Dados carregados: {len(df)} registros")
        print(f"📅 Período: {df['data'].min()} a {df['data'].max()}")
        print(f"🏘️ Municípios: {df['municipio'].nunique()}")
        
        # 2. Testar Feature Engineering
        print("\n🔧 2. Testando Feature Engineering...")
        from features.feature_engineering import FeatureEngineer
        
        feature_engineer = FeatureEngineer()
        
        # Criar features
        df_features = feature_engineer.create_lag_features(
            df, ['casos_confirmados', 'temperatura_media', 'precipitacao'], [1, 2, 3, 4]
        )
        
        df_features = feature_engineer.create_rolling_features(
            df_features, ['casos_confirmados'], [2, 4, 8]
        )
        
        df_features = feature_engineer.create_temporal_features(df_features)
        
        df_features = feature_engineer.create_interaction_features(df_features)
        
        print(f"✅ Features criadas: {len(df_features.columns)} colunas")
        print(f"📈 Features numéricas: {len(df_features.select_dtypes(include=[np.number]).columns)}")
        
        # 3. Preparar dados para treinamento
        print("\n🎯 3. Preparando dados para treinamento...")
        
        # Remover linhas com NaN (devido aos lags)
        df_clean = df_features.dropna()
        print(f"📊 Dados limpos: {len(df_clean)} registros")
        
        # Separar features e target
        feature_cols = [col for col in df_clean.columns 
                       if col not in ['municipio', 'data', 'risco_futuro', 'ano', 'mes', 'semana']]
        
        X = df_clean[feature_cols]
        y = df_clean['risco_futuro']
        
        print(f"🔢 Features: {X.shape[1]}")
        print(f"🎯 Target: {y.nunique()} classes")
        print(f"📊 Distribuição do target:")
        print(y.value_counts())
        
        # 4. Treinar modelo
        print("\n🚀 4. Treinando modelo...")
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
        
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"📚 Treino: {len(X_train)} amostras")
        print(f"🧪 Teste: {len(X_test)} amostras")
        
        # Treinar modelo
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # 5. Avaliar modelo
        print("\n📊 5. Avaliando modelo...")
        
        # Predições
        y_pred = model.predict(X_test)
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"🎯 Acurácia: {accuracy:.3f}")
        print("\n📋 Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        print("\n🔢 Matriz de Confusão:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # 6. Feature Importance
        print("\n🔍 6. Importância das Features:")
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("Top 10 features mais importantes:")
        print(feature_importance.head(10))
        
        # 7. Salvar modelo
        print("\n💾 7. Salvando modelo...")
        os.makedirs('models', exist_ok=True)
        model_path = 'models/test_model.joblib'
        
        import joblib
        joblib.dump(model, model_path)
        print(f"✅ Modelo salvo em: {model_path}")
        
        # 8. Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO DO TESTE ML")
        print("=" * 50)
        print(f"✅ Dados processados: {len(df_clean)} registros")
        print(f"✅ Features criadas: {len(feature_cols)}")
        print(f"✅ Acurácia do modelo: {accuracy:.3f}")
        print(f"✅ Modelo salvo com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_module()
    sys.exit(0 if success else 1)
