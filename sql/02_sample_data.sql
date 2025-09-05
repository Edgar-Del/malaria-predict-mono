-- Dados de exemplo para desenvolvimento e testes
-- Inserir dados históricos de exemplo (últimas 52 semanas)

-- Função para gerar dados de exemplo
DO $$
DECLARE
    municipio_record RECORD;
    semana_atual INTEGER;
    ano_atual INTEGER;
    casos_base INTEGER;
    casos_variacao INTEGER;
    chuva_base DECIMAL;
    temp_base DECIMAL;
BEGIN
    -- Obter ano e semana atual
    ano_atual := EXTRACT(YEAR FROM CURRENT_DATE);
    semana_atual := EXTRACT(WEEK FROM CURRENT_DATE);
    
    -- Para cada município
    FOR municipio_record IN SELECT id, nome FROM municipios LOOP
        -- Definir valores base por município
        CASE municipio_record.nome
            WHEN 'Kuito' THEN
                casos_base := 150;
                chuva_base := 120.0;
                temp_base := 22.5;
            WHEN 'Camacupa' THEN
                casos_base := 80;
                chuva_base := 100.0;
                temp_base := 23.0;
            WHEN 'Andulo' THEN
                casos_base := 90;
                chuva_base := 110.0;
                temp_base := 22.0;
            ELSE
                casos_base := 50;
                chuva_base := 90.0;
                temp_base := 23.5;
        END CASE;
        
        -- Inserir dados para as últimas 52 semanas
        FOR i IN 0..51 LOOP
            -- Calcular semana e ano
            DECLARE
                semana_dados INTEGER;
                ano_dados INTEGER;
            BEGIN
                semana_dados := semana_atual - i;
                ano_dados := ano_atual;
                
                -- Ajustar ano se necessário
                IF semana_dados <= 0 THEN
                    semana_dados := semana_dados + 52;
                    ano_dados := ano_dados - 1;
                END IF;
                
                -- Gerar variação aleatória nos dados
                casos_variacao := casos_base + (RANDOM() * 50 - 25)::INTEGER;
                IF casos_variacao < 0 THEN casos_variacao := 0; END IF;
                
                -- Inserir dados da semana
                INSERT INTO series_semanais (
                    municipio_id,
                    ano_semana,
                    casos,
                    chuva_mm,
                    temp_media_c,
                    temp_min_c,
                    temp_max_c,
                    umidade_relativa
                ) VALUES (
                    municipio_record.id,
                    ano_dados || '-' || LPAD(semana_dados::TEXT, 2, '0'),
                    casos_variacao,
                    chuva_base + (RANDOM() * 40 - 20),
                    temp_base + (RANDOM() * 4 - 2),
                    temp_base + (RANDOM() * 4 - 2) + 5,
                    temp_base + (RANDOM() * 4 - 2) - 5,
                    60 + (RANDOM() * 30)
                ) ON CONFLICT (municipio_id, ano_semana) DO NOTHING;
            END;
        END LOOP;
    END LOOP;
END $$;

-- Inserir algumas previsões de exemplo
INSERT INTO previsoes (
    municipio_id,
    ano_semana_prevista,
    classe_risco,
    score_risco,
    probabilidade_baixo,
    probabilidade_medio,
    probabilidade_alto,
    modelo_versao,
    modelo_tipo
) 
SELECT 
    m.id,
    TO_CHAR(CURRENT_DATE + INTERVAL '1 week', 'IYYY-IW') as proxima_semana,
    CASE 
        WHEN RANDOM() < 0.3 THEN 'baixo'
        WHEN RANDOM() < 0.7 THEN 'medio'
        ELSE 'alto'
    END as classe_risco,
    RANDOM() as score_risco,
    RANDOM() * 0.4 as prob_baixo,
    RANDOM() * 0.4 + 0.3 as prob_medio,
    RANDOM() * 0.3 + 0.2 as prob_alto,
    'v1.0.0' as modelo_versao,
    'RandomForest' as modelo_tipo
FROM municipios m
ON CONFLICT (municipio_id, ano_semana_prevista, modelo_versao) DO NOTHING;

-- Inserir métricas de exemplo
INSERT INTO metricas_modelo (
    modelo_versao,
    modelo_tipo,
    data_treinamento,
    accuracy,
    precision_macro,
    recall_macro,
    f1_macro,
    precision_baixo,
    recall_baixo,
    f1_baixo,
    precision_medio,
    recall_medio,
    f1_medio,
    precision_alto,
    recall_alto,
    f1_alto,
    parametros
) VALUES (
    'v1.0.0',
    'RandomForest',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    0.8234,
    0.8156,
    0.8201,
    0.8178,
    0.8500,
    0.8200,
    0.8348,
    0.7800,
    0.8100,
    0.7949,
    0.8200,
    0.8300,
    0.8250,
    '{"n_estimators": 100, "max_depth": 10, "random_state": 42}'::jsonb
);
