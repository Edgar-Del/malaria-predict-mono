-- Schema do banco de dados para o Sistema de Previsão de Malária (Bié)
-- Criado em: 2024

-- Tabela de municípios do Bié
CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    cod_ibge_local VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    populacao INTEGER,
    area_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de séries semanais (dados históricos)
CREATE TABLE IF NOT EXISTS series_semanais (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL REFERENCES municipios(id),
    ano_semana VARCHAR(7) NOT NULL, -- formato: YYYY-WW
    casos INTEGER NOT NULL DEFAULT 0,
    chuva_mm DECIMAL(8, 2),
    temp_media_c DECIMAL(5, 2),
    temp_min_c DECIMAL(5, 2),
    temp_max_c DECIMAL(5, 2),
    umidade_relativa DECIMAL(5, 2),
    -- Features calculadas
    casos_lag1 INTEGER,
    casos_lag2 INTEGER,
    casos_lag3 INTEGER,
    casos_lag4 INTEGER,
    chuva_lag1 DECIMAL(8, 2),
    temp_lag1 DECIMAL(5, 2),
    casos_media_2s DECIMAL(8, 2),
    casos_media_4s DECIMAL(8, 2),
    chuva_media_2s DECIMAL(8, 2),
    chuva_media_4s DECIMAL(8, 2),
    temp_media_2s DECIMAL(5, 2),
    temp_media_4s DECIMAL(5, 2),
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(municipio_id, ano_semana)
);

-- Tabela de previsões
CREATE TABLE IF NOT EXISTS previsoes (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL REFERENCES municipios(id),
    ano_semana_prevista VARCHAR(7) NOT NULL, -- formato: YYYY-WW
    classe_risco VARCHAR(10) NOT NULL CHECK (classe_risco IN ('baixo', 'medio', 'alto')),
    score_risco DECIMAL(4, 3) NOT NULL CHECK (score_risco >= 0 AND score_risco <= 1),
    probabilidade_baixo DECIMAL(4, 3),
    probabilidade_medio DECIMAL(4, 3),
    probabilidade_alto DECIMAL(4, 3),
    modelo_versao VARCHAR(50) NOT NULL,
    modelo_tipo VARCHAR(50) NOT NULL,
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(municipio_id, ano_semana_prevista, modelo_versao)
);

-- Tabela de métricas do modelo
CREATE TABLE IF NOT EXISTS metricas_modelo (
    id SERIAL PRIMARY KEY,
    modelo_versao VARCHAR(50) NOT NULL,
    modelo_tipo VARCHAR(50) NOT NULL,
    data_treinamento TIMESTAMP NOT NULL,
    -- Métricas gerais
    accuracy DECIMAL(5, 4),
    precision_macro DECIMAL(5, 4),
    recall_macro DECIMAL(5, 4),
    f1_macro DECIMAL(5, 4),
    -- Métricas por classe
    precision_baixo DECIMAL(5, 4),
    recall_baixo DECIMAL(5, 4),
    f1_baixo DECIMAL(5, 4),
    precision_medio DECIMAL(5, 4),
    recall_medio DECIMAL(5, 4),
    f1_medio DECIMAL(5, 4),
    precision_alto DECIMAL(5, 4),
    recall_alto DECIMAL(5, 4),
    f1_alto DECIMAL(5, 4),
    -- Parâmetros do modelo
    parametros JSONB,
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de alertas enviados
CREATE TABLE IF NOT EXISTS alertas_enviados (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER NOT NULL REFERENCES municipios(id),
    ano_semana VARCHAR(7) NOT NULL,
    classe_risco VARCHAR(10) NOT NULL,
    score_risco DECIMAL(4, 3) NOT NULL,
    email_destinatarios TEXT NOT NULL,
    assunto VARCHAR(200) NOT NULL,
    enviado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_envio VARCHAR(20) DEFAULT 'enviado' CHECK (status_envio IN ('enviado', 'falhou', 'pendente'))
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_series_semanais_municipio_ano ON series_semanais(municipio_id, ano_semana);
CREATE INDEX IF NOT EXISTS idx_series_semanais_ano ON series_semanais(ano_semana);
CREATE INDEX IF NOT EXISTS idx_previsoes_municipio_ano ON previsoes(municipio_id, ano_semana_prevista);
CREATE INDEX IF NOT EXISTS idx_previsoes_ano ON previsoes(ano_semana_prevista);
CREATE INDEX IF NOT EXISTS idx_metricas_modelo_versao ON metricas_modelo(modelo_versao);
CREATE INDEX IF NOT EXISTS idx_alertas_municipio_ano ON alertas_enviados(municipio_id, ano_semana);

-- Inserir municípios do Bié
INSERT INTO municipios (nome, cod_ibge_local, latitude, longitude, populacao, area_km2) VALUES
('Kuito', 'BIE001', -12.3833, 17.0000, 185000, 4814.0),
('Camacupa', 'BIE002', -12.0167, 17.4833, 45000, 7420.0),
('Catabola', 'BIE003', -12.1500, 17.2833, 35000, 3850.0),
('Chinguar', 'BIE004', -12.5500, 16.3333, 28000, 4200.0),
('Chitembo', 'BIE005', -13.3167, 16.0000, 22000, 3500.0),
('Cuemba', 'BIE006', -12.8333, 16.8333, 18000, 2800.0),
('Cunhinga', 'BIE007', -12.2500, 16.7500, 25000, 3200.0),
('Nharea', 'BIE008', -11.8333, 16.9167, 30000, 4100.0),
('Andulo', 'BIE009', -11.4833, 16.4167, 40000, 5200.0)
ON CONFLICT (nome) DO NOTHING;
