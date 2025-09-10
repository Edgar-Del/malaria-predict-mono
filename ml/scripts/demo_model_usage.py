#!/usr/bin/env python3
"""
Demonstração de uso do modelo ML treinado com dados reais
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

def load_model():
    """Carrega o modelo e encoders"""
    print("📦 Carregando modelo...")
    
    model = joblib.load("models/malaria_risk_model_real.pkl")
    le_risco = joblib.load("models/label_encoder_risco.pkl")
    le_municipio = joblib.load("models/label_encoder_municipio.pkl")
    
    print("✅ Modelo carregado!")
    return model, le_risco, le_municipio

def predict_single_case(model, le_risco, le_municipio, municipio, ano, semana, 
                       temperatura, precipitacao, casos_anteriores):
    """Faz predição para um caso específico"""
    
    # Criar DataFrame com os dados
    data = {
        'Ano': [ano],
        'Semana': [semana],
        'Municipio': [municipio],
        'Casos_Malaria': [casos_anteriores],
        'Temperatura_Media_C': [temperatura],
        'Precipitacao_mm': [precipitacao]
    }
    
    df = pd.DataFrame(data)
    
    # Criar features (simplificado)
    df['semana_sin'] = np.sin(2 * np.pi * df['Semana'] / 52)
    df['semana_cos'] = np.cos(2 * np.pi * df['Semana'] / 52)
    df['tendencia'] = (df['Ano'] - 2020) * 52 + df['Semana']
    df['estacao'] = ((df['Semana'] - 1) // 13) + 1
    df['temp_norm'] = (df['Temperatura_Media_C'] - 23.0) / 1.0  # Valores aproximados
    df['precip_norm'] = (df['Precipitacao_mm'] - 60.0) / 20.0
    df['casos_lag1'] = casos_anteriores
    df['casos_lag2'] = casos_anteriores
    df['casos_ma3'] = casos_anteriores
    df['casos_ma5'] = casos_anteriores
    df['municipio_encoded'] = le_municipio.transform([municipio])[0]
    df['temp_precip_interaction'] = df['Temperatura_Media_C'] * df['Precipitacao_mm']
    df['casos_temp_interaction'] = df['Casos_Malaria'] * df['Temperatura_Media_C']
    
    # Features para predição
    feature_columns = [
        'Ano', 'Semana', 'Temperatura_Media_C', 'Precipitacao_mm',
        'semana_sin', 'semana_cos', 'tendencia', 'estacao',
        'temp_norm', 'precip_norm', 'casos_lag1', 'casos_lag2',
        'casos_ma3', 'casos_ma5', 'municipio_encoded',
        'temp_precip_interaction', 'casos_temp_interaction'
    ]
    
    X = df[feature_columns]
    
    # Fazer predição
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    
    # Decodificar
    risk_predicted = le_risco.inverse_transform([prediction])[0]
    
    return risk_predicted, probabilities

def main():
    """Demonstração principal"""
    print("🚀 DEMONSTRAÇÃO DO MODELO ML - MALÁRIA BIÉ")
    print("=" * 50)
    
    # Carregar modelo
    model, le_risco, le_municipio = load_model()
    
    print(f"\n🎯 Classes de risco: {le_risco.classes_}")
    print(f"🏘️ Municípios disponíveis: {le_municipio.classes_}")
    
    # Exemplos de predição
    print("\n" + "=" * 50)
    print("🔮 EXEMPLOS DE PREDIÇÃO")
    print("=" * 50)
    
    examples = [
        {
            'municipio': 'Cuito',
            'ano': 2024,
            'semana': 45,
            'temperatura': 24.5,
            'precipitacao': 80.0,
            'casos_anteriores': 1200
        },
        {
            'municipio': 'Nharea',
            'ano': 2024,
            'semana': 45,
            'temperatura': 25.0,
            'precipitacao': 95.0,
            'casos_anteriores': 1800
        },
        {
            'municipio': 'Catabola',
            'ano': 2024,
            'semana': 45,
            'temperatura': 22.0,
            'precipitacao': 30.0,
            'casos_anteriores': 600
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📊 Exemplo {i}:")
        print(f"   Município: {example['municipio']}")
        print(f"   Semana: {example['ano']}-{example['semana']}")
        print(f"   Temperatura: {example['temperatura']}°C")
        print(f"   Precipitação: {example['precipitacao']}mm")
        print(f"   Casos anteriores: {example['casos_anteriores']}")
        
        # Fazer predição
        risk, probs = predict_single_case(
            model, le_risco, le_municipio,
            example['municipio'], example['ano'], example['semana'],
            example['temperatura'], example['precipitacao'], example['casos_anteriores']
        )
        
        print(f"   🎯 Risco predito: {risk}")
        print(f"   📊 Probabilidades:")
        for j, class_name in enumerate(le_risco.classes_):
            print(f"      {class_name}: {probs[j]:.3f}")
    
    # Interface interativa
    print("\n" + "=" * 50)
    print("🎮 INTERFACE INTERATIVA")
    print("=" * 50)
    print("Digite os dados para fazer uma predição personalizada:")
    print("(Pressione Enter para usar valores padrão)")
    
    try:
        municipio = input(f"Município {list(le_municipio.classes_)}: ").strip() or "Cuito"
        ano = int(input("Ano (2020-2024): ") or "2024")
        semana = int(input("Semana (1-52): ") or "45")
        temperatura = float(input("Temperatura média (°C): ") or "24.0")
        precipitacao = float(input("Precipitação (mm): ") or "60.0")
        casos_anteriores = int(input("Casos da semana anterior: ") or "1000")
        
        # Fazer predição
        risk, probs = predict_single_case(
            model, le_risco, le_municipio,
            municipio, ano, semana, temperatura, precipitacao, casos_anteriores
        )
        
        print(f"\n🎯 RESULTADO:")
        print(f"   Risco predito: {risk}")
        print(f"   Confiança: {max(probs):.1%}")
        
        # Interpretação
        if risk == "Alto":
            print("   ⚠️ ATENÇÃO: Risco alto de malária!")
            print("   📋 Recomendações:")
            print("      - Intensificar campanhas de prevenção")
            print("      - Distribuir mosquiteiros")
            print("      - Monitorar casos diariamente")
        elif risk == "Médio":
            print("   ⚡ Risco médio - monitoramento necessário")
            print("   📋 Recomendações:")
            print("      - Manter vigilância epidemiológica")
            print("      - Preparar recursos para possível aumento")
        else:
            print("   ✅ Risco baixo - situação controlada")
            print("   📋 Recomendações:")
            print("      - Manter medidas preventivas básicas")
            print("      - Continuar monitoramento")
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Demonstração finalizada!")
    
    print("\n🎉 Obrigado por usar o modelo de predição de malária!")

if __name__ == "__main__":
    main()
