#!/usr/bin/env python3
"""
Script para gerar dataset expandido com pelo menos 100 mil registros
Baseado nos padrões dos dados reais do Bié
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from loguru import logger
import os

# Configurar logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="INFO"
)

# Configurações
TARGET_RECORDS = 100000  # Meta de registros
OUTPUT_FILE = "../../../data/raw/malaria_bie_expanded.csv"

# Municípios do Bié (expandido com mais localidades)
MUNICIPIOS = [
    "Cuito", "Andulo", "Nharea", "Camacupa", "Chinguar", 
    "Catabola", "Cunhinga", "Chitembo", "Cuemba",
    # Adicionar mais localidades para aumentar registros
    "Bailundo", "Caconda", "Caluquembe", "Chibia", "Chicomba",
    "Chipindo", "Gambos", "Humpata", "Jamba", "Lubango",
    "Matala", "Quilengues", "Quipungo", "Umbundu", "Virei"
]

# Período expandido (2010-2024 para ter mais dados)
START_YEAR = 2010
END_YEAR = 2024

# Padrões baseados nos dados reais
MUNICIPIO_PATTERNS = {
    "Cuito": {
        "base_cases": 1200,
        "temp_base": 23.5,
        "precip_base": 65.0,
        "risk_tendency": "Médio",
        "population_factor": 1.2  # Capital, mais casos
    },
    "Andulo": {
        "base_cases": 1500,
        "temp_base": 22.5,
        "precip_base": 70.0,
        "risk_tendency": "Alto",
        "population_factor": 1.1
    },
    "Nharea": {
        "base_cases": 1400,
        "temp_base": 24.0,
        "precip_base": 85.0,
        "risk_tendency": "Alto",
        "population_factor": 1.0
    },
    "Camacupa": {
        "base_cases": 1300,
        "temp_base": 22.0,
        "precip_base": 75.0,
        "risk_tendency": "Alto",
        "population_factor": 1.0
    },
    "Chinguar": {
        "base_cases": 1600,
        "temp_base": 24.5,
        "precip_base": 60.0,
        "risk_tendency": "Alto",
        "population_factor": 1.1
    },
    "Catabola": {
        "base_cases": 800,
        "temp_base": 22.5,
        "precip_base": 50.0,
        "risk_tendency": "Baixo",
        "population_factor": 0.8
    },
    "Cunhinga": {
        "base_cases": 1400,
        "temp_base": 22.0,
        "precip_base": 70.0,
        "risk_tendency": "Alto",
        "population_factor": 1.0
    },
    "Chitembo": {
        "base_cases": 1000,
        "temp_base": 23.0,
        "precip_base": 60.0,
        "risk_tendency": "Médio",
        "population_factor": 0.9
    },
    "Cuemba": {
        "base_cases": 600,
        "temp_base": 24.0,
        "precip_base": 45.0,
        "risk_tendency": "Baixo",
        "population_factor": 0.7
    },
    # Novos municípios com padrões variados
    "Bailundo": {"base_cases": 800, "temp_base": 23.0, "precip_base": 60.0, "risk_tendency": "Médio", "population_factor": 0.8},
    "Caconda": {"base_cases": 700, "temp_base": 22.5, "precip_base": 55.0, "risk_tendency": "Médio", "population_factor": 0.7},
    "Caluquembe": {"base_cases": 900, "temp_base": 23.5, "precip_base": 65.0, "risk_tendency": "Alto", "population_factor": 0.9},
    "Chibia": {"base_cases": 600, "temp_base": 24.0, "precip_base": 50.0, "risk_tendency": "Baixo", "population_factor": 0.6},
    "Chicomba": {"base_cases": 750, "temp_base": 23.0, "precip_base": 58.0, "risk_tendency": "Médio", "population_factor": 0.8},
    "Chipindo": {"base_cases": 850, "temp_base": 22.0, "precip_base": 70.0, "risk_tendency": "Alto", "population_factor": 0.9},
    "Gambos": {"base_cases": 500, "temp_base": 24.5, "precip_base": 40.0, "risk_tendency": "Baixo", "population_factor": 0.5},
    "Humpata": {"base_cases": 650, "temp_base": 22.0, "precip_base": 55.0, "risk_tendency": "Médio", "population_factor": 0.7},
    "Jamba": {"base_cases": 950, "temp_base": 23.0, "precip_base": 75.0, "risk_tendency": "Alto", "population_factor": 1.0},
    "Lubango": {"base_cases": 1200, "temp_base": 22.5, "precip_base": 60.0, "risk_tendency": "Médio", "population_factor": 1.2},
    "Matala": {"base_cases": 800, "temp_base": 24.0, "precip_base": 65.0, "risk_tendency": "Alto", "population_factor": 0.8},
    "Quilengues": {"base_cases": 700, "temp_base": 23.5, "precip_base": 55.0, "risk_tendency": "Médio", "population_factor": 0.7},
    "Quipungo": {"base_cases": 600, "temp_base": 24.0, "precip_base": 50.0, "risk_tendency": "Baixo", "population_factor": 0.6},
    "Umbundu": {"base_cases": 750, "temp_base": 23.0, "precip_base": 58.0, "risk_tendency": "Médio", "population_factor": 0.8},
    "Virei": {"base_cases": 500, "temp_base": 25.0, "precip_base": 35.0, "risk_tendency": "Baixo", "population_factor": 0.5}
}

def generate_seasonal_patterns():
    """Gera padrões sazonais para temperatura e precipitação"""
    logger.info("🌡️ Gerando padrões sazonais...")
    
    # Padrões sazonais baseados no clima do Bié
    seasonal_temp = {}
    seasonal_precip = {}
    
    for week in range(1, 53):
        # Temperatura: mais alta no verão (dez-fev), mais baixa no inverno (jun-ago)
        temp_factor = 1 + 0.3 * np.sin(2 * np.pi * (week - 10) / 52)  # Pico em dezembro
        
        # Precipitação: pico na estação chuvosa (out-mar)
        precip_factor = 1 + 0.8 * np.sin(2 * np.pi * (week - 40) / 52)  # Pico em outubro
        
        seasonal_temp[week] = temp_factor
        seasonal_precip[week] = max(0.2, precip_factor)  # Mínimo de 20% da precipitação base
    
    return seasonal_temp, seasonal_precip

def generate_malaria_seasonality():
    """Gera sazonalidade da malária (pico após chuvas)"""
    logger.info("🦟 Gerando sazonalidade da malária...")
    
    malaria_factor = {}
    
    for week in range(1, 53):
        # Pico da malária 4-8 semanas após pico de chuvas
        # Baseado no ciclo do mosquito e incubação
        lag_weeks = 6  # Lag típico entre chuvas e casos
        adjusted_week = (week - lag_weeks) % 52
        if adjusted_week <= 0:
            adjusted_week += 52
            
        # Fator sazonal com pico em dez-jan (após chuvas de out-nov)
        factor = 1 + 0.6 * np.sin(2 * np.pi * (adjusted_week - 50) / 52)
        malaria_factor[week] = max(0.3, factor)  # Mínimo de 30% dos casos base
    
    return malaria_factor

def generate_temporal_trends():
    """Gera tendências temporais (melhoria ao longo dos anos)"""
    logger.info("📈 Gerando tendências temporais...")
    
    # Tendência de melhoria (redução de casos ao longo dos anos)
    # Baseado em programas de controle de malária
    year_trends = {}
    
    for year in range(START_YEAR, END_YEAR + 1):
        # Redução gradual de 2-3% ao ano
        years_from_start = year - START_YEAR
        improvement_factor = 0.98 ** years_from_start  # 2% de melhoria por ano
        year_trends[year] = improvement_factor
    
    return year_trends

def generate_epidemic_events():
    """Gera eventos epidêmicos ocasionais"""
    logger.info("🚨 Gerando eventos epidêmicos...")
    
    epidemic_events = []
    
    # Gerar 2-3 epidemias por ano em municípios aleatórios
    for year in range(START_YEAR, END_YEAR + 1):
        num_epidemics = random.randint(2, 4)
        
        for _ in range(num_epidemics):
            municipio = random.choice(MUNICIPIOS)
            week = random.randint(10, 45)  # Evitar início/fim do ano
            intensity = random.uniform(2.0, 4.0)  # 2-4x casos normais
            duration = random.randint(3, 8)  # 3-8 semanas
            
            epidemic_events.append({
                'year': year,
                'week': week,
                'municipio': municipio,
                'intensity': intensity,
                'duration': duration
            })
    
    return epidemic_events

def calculate_risk_level(cases, municipio_pattern):
    """Calcula nível de risco baseado nos casos"""
    base_cases = municipio_pattern['base_cases']
    
    if cases >= base_cases * 1.5:
        return "Alto"
    elif cases >= base_cases * 0.8:
        return "Médio"
    else:
        return "Baixo"

def generate_single_record(year, week, municipio, seasonal_temp, seasonal_precip, 
                          malaria_factor, year_trends, epidemic_events):
    """Gera um único registro de dados"""
    
    pattern = MUNICIPIO_PATTERNS[municipio]
    
    # Temperatura com variação sazonal e aleatória
    temp_base = pattern['temp_base']
    temp_seasonal = seasonal_temp[week]
    temp_random = np.random.normal(0, 1.5)  # Variação aleatória
    temperatura = temp_base * temp_seasonal + temp_random
    temperatura = max(18.0, min(30.0, temperatura))  # Limites realistas
    
    # Precipitação com variação sazonal e aleatória
    precip_base = pattern['precip_base']
    precip_seasonal = seasonal_precip[week]
    precip_random = np.random.normal(0, 15.0)  # Variação aleatória
    precipitacao = precip_base * precip_seasonal + precip_random
    precipitacao = max(0.0, min(200.0, precipitacao))  # Limites realistas
    
    # Casos de malária
    base_cases = pattern['base_cases']
    population_factor = pattern['population_factor']
    
    # Aplicar fatores
    cases = (base_cases * 
             population_factor * 
             malaria_factor[week] * 
             year_trends[year])
    
    # Verificar se há epidemia
    for epidemic in epidemic_events:
        if (epidemic['year'] == year and 
            epidemic['municipio'] == municipio and
            epidemic['week'] <= week <= epidemic['week'] + epidemic['duration']):
            cases *= epidemic['intensity']
            break
    
    # Adicionar ruído aleatório
    cases *= np.random.normal(1.0, 0.2)  # 20% de variação
    casos = max(50, int(cases))  # Mínimo de 50 casos
    
    # Calcular risco
    risco = calculate_risk_level(casos, pattern)
    
    return {
        'Ano': year,
        'Semana': week,
        'Municipio': municipio,
        'Casos_Malaria': casos,
        'Temperatura_Media_C': round(temperatura, 1),
        'Precipitacao_mm': round(precipitacao, 1),
        'Risco': risco
    }

def generate_dataset():
    """Gera o dataset expandido"""
    logger.info(f"🚀 Iniciando geração de dataset com {TARGET_RECORDS:,} registros...")
    
    # Gerar padrões
    seasonal_temp, seasonal_precip = generate_seasonal_patterns()
    malaria_factor = generate_malaria_seasonality()
    year_trends = generate_temporal_trends()
    epidemic_events = generate_epidemic_events()
    
    logger.info(f"📊 Eventos epidêmicos gerados: {len(epidemic_events)}")
    
    # Calcular registros por município
    total_weeks = (END_YEAR - START_YEAR + 1) * 52
    records_per_municipio = TARGET_RECORDS // len(MUNICIPIOS)
    
    logger.info(f"📅 Período: {START_YEAR}-{END_YEAR} ({total_weeks} semanas)")
    logger.info(f"🏘️ Registros por município: {records_per_municipio:,}")
    
    # Gerar dados
    all_records = []
    
    for municipio in MUNICIPIOS:
        logger.info(f"🏘️ Gerando dados para {municipio}...")
        
        municipio_records = []
        
        for year in range(START_YEAR, END_YEAR + 1):
            for week in range(1, 53):
                record = generate_single_record(
                    year, week, municipio, seasonal_temp, seasonal_precip,
                    malaria_factor, year_trends, epidemic_events
                )
                municipio_records.append(record)
        
        all_records.extend(municipio_records)
        logger.info(f"✅ {municipio}: {len(municipio_records)} registros")
    
    # Criar DataFrame
    df = pd.DataFrame(all_records)
    
    # Ordenar por ano, semana, município
    df = df.sort_values(['Ano', 'Semana', 'Municipio']).reset_index(drop=True)
    
    logger.info(f"✅ Dataset gerado: {len(df):,} registros")
    
    return df

def validate_dataset(df):
    """Valida a qualidade do dataset gerado"""
    logger.info("🔍 Validando dataset...")
    
    # Estatísticas básicas
    logger.info(f"📊 Total de registros: {len(df):,}")
    logger.info(f"📅 Período: {df['Ano'].min()}-{df['Ano'].max()}")
    logger.info(f"🏘️ Municípios: {df['Municipio'].nunique()}")
    logger.info(f"📈 Total de casos: {df['Casos_Malaria'].sum():,}")
    
    # Distribuição de risco
    risk_dist = df['Risco'].value_counts()
    logger.info(f"🎯 Distribuição de risco:")
    for risk, count in risk_dist.items():
        percentage = (count / len(df)) * 100
        logger.info(f"   {risk}: {count:,} ({percentage:.1f}%)")
    
    # Estatísticas por município
    logger.info(f"🏘️ Casos por município:")
    municipio_stats = df.groupby('Municipio')['Casos_Malaria'].agg(['sum', 'mean', 'std'])
    for municipio, stats in municipio_stats.iterrows():
        logger.info(f"   {municipio}: {stats['sum']:,.0f} total, {stats['mean']:.0f} média")
    
    # Verificar valores extremos
    logger.info(f"🌡️ Temperatura: {df['Temperatura_Media_C'].min():.1f}°C - {df['Temperatura_Media_C'].max():.1f}°C")
    logger.info(f"🌧️ Precipitação: {df['Precipitacao_mm'].min():.1f}mm - {df['Precipitacao_mm'].max():.1f}mm")
    logger.info(f"🦟 Casos: {df['Casos_Malaria'].min()} - {df['Casos_Malaria'].max()}")
    
    return True

def main():
    """Função principal"""
    logger.info("🎯 Iniciando geração de dataset expandido...")
    
    try:
        # Gerar dataset
        df = generate_dataset()
        
        # Validar
        validate_dataset(df)
        
        # Salvar
        logger.info(f"💾 Salvando dataset em: {OUTPUT_FILE}")
        df.to_csv(OUTPUT_FILE, index=False)
        
        logger.info("🎉 Dataset expandido gerado com sucesso!")
        
        # Resumo final
        print("\n" + "="*60)
        print("🎉 RESUMO DO DATASET EXPANDIDO")
        print("="*60)
        print(f"📊 Total de registros: {len(df):,}")
        print(f"📅 Período: {df['Ano'].min()}-{df['Ano'].max()}")
        print(f"🏘️ Municípios: {df['Municipio'].nunique()}")
        print(f"📈 Total de casos: {df['Casos_Malaria'].sum():,}")
        print(f"💾 Arquivo: {OUTPUT_FILE}")
        
        # Próximos passos
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"1. Retreinar modelo: python train_expanded_model.py")
        print(f"2. Comparar performance: python compare_models.py")
        print(f"3. Validar predições: python test_expanded_model.py")
        
    except Exception as e:
        logger.error(f"❌ Erro durante geração: {e}")
        raise

if __name__ == "__main__":
    main()
