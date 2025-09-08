#!/usr/bin/env python3
"""
Script para gerar dados de exemplo para teste do módulo ML.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Adicionar o diretório ml ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_sample_data():
    """Gera dados de exemplo para teste do modelo."""
    
    print("Gerando dados de exemplo...")
    
    # Municípios do Bié
    municipios = [
        "Andulo", "Camacupa", "Catabola", "Chinguar", "Chitembo",
        "Cuemba", "Cunhinga", "Kuito", "Nharea"
    ]
    
    # Período de 2 anos (104 semanas)
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(104)]
    
    data = []
    
    for municipio in municipios:
        for i, date in enumerate(dates):
            # Simular padrões sazonais e climáticos
            week_of_year = date.isocalendar()[1]
            
            # Fatores sazonais (maior risco na estação chuvosa)
            seasonal_factor = 1 + 0.5 * np.sin(2 * np.pi * week_of_year / 52)
            
            # Fatores climáticos simulados
            temperatura = 20 + 10 * np.sin(2 * np.pi * week_of_year / 52) + np.random.normal(0, 2)
            chuva = max(0, 50 + 100 * np.sin(2 * np.pi * week_of_year / 52) + np.random.normal(0, 20))
            umidade = 60 + 20 * np.sin(2 * np.pi * week_of_year / 52) + np.random.normal(0, 5)
            
            # Casos históricos (baseado em fatores sazonais + ruído)
            casos_base = int(10 + 20 * seasonal_factor + np.random.poisson(5))
            casos_confirmados = max(0, casos_base)
            
            # Risco futuro (target) - baseado em casos atuais e fatores climáticos
            if casos_confirmados > 25 or chuva > 150:
                risco_futuro = "alto"
            elif casos_confirmados > 15 or chuva > 100:
                risco_futuro = "médio"
            else:
                risco_futuro = "baixo"
            
            data.append({
                'municipio': municipio,
                'data': date,
                'ano': date.year,
                'mes': date.month,
                'semana': week_of_year,
                'casos_confirmados': casos_confirmados,
                'temperatura_media': round(temperatura, 1),
                'precipitacao': round(chuva, 1),
                'umidade_relativa': round(umidade, 1),
                'risco_futuro': risco_futuro
            })
    
    df = pd.DataFrame(data)
    
    # Salvar dados
    os.makedirs('../data/processed', exist_ok=True)
    output_path = '../data/processed/malaria_data_sample.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Dados gerados: {len(df)} registros")
    print(f"📁 Salvo em: {output_path}")
    print(f"📊 Municípios: {len(municipios)}")
    print(f"📅 Período: {df['data'].min()} a {df['data'].max()}")
    print(f"🎯 Distribuição de risco:")
    print(df['risco_futuro'].value_counts())
    
    return df

if __name__ == "__main__":
    generate_sample_data()
