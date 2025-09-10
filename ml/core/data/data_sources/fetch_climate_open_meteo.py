#!/usr/bin/env python3
"""
Coleta dados climáticos reais (históricos) via Open-Meteo API
para os municípios da província do Bié e salva em data/raw/clima_bie.csv

Fonte: https://open-meteo.com/
Termos: API pública e gratuita, sem chave.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

import requests


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
OUTPUT_FILE = os.path.join(DATA_DIR, "clima_bie.csv")


@dataclass(frozen=True)
class Municipio:
    nome: str
    lat: float
    lon: float


# Coordenadas aproximadas dos municípios do Bié (fonte: várias gazetteers públicas)
MUNICIPIOS: List[Municipio] = [
    Municipio("Kuito", -12.3833, 16.9333),
    Municipio("Andulo", -11.2667, 16.0167),
    Municipio("Camacupa", -12.0167, 17.4833),
    Municipio("Catabola", -12.1500, 17.2833),
    Municipio("Chinguar", -12.5333, 16.3667),
    Municipio("Chitembo", -13.5667, 17.1333),
    Municipio("Cuemba", -12.1500, 18.0167),
    Municipio("Cunhinga", -12.1000, 16.9667),
    Municipio("Nharea", -11.6833, 16.8167),
]


def fetch_open_meteo_daily(lat: float, lon: float, start: str, end: str) -> Dict[str, List]:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        # Variáveis diárias
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "relative_humidity_2m_mean",
        ],
        "timezone": "Africa/Luanda",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json().get("daily", {})


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Janela histórica (ajuste conforme necessário)
    start = "2018-01-01"
    end = date.today().isoformat()

    # Cabeçalho do CSV
    header = [
        "municipio",
        "data",
        "temperatura_media",
        "precipitacao",
        "umidade_relativa",
    ]

    rows: List[List] = []

    for m in MUNICIPIOS:
        data = fetch_open_meteo_daily(m.lat, m.lon, start, end)
        dates = data.get("time", [])
        tmean = data.get("temperature_2m_mean", [])
        prcp = data.get("precipitation_sum", [])
        rh = data.get("relative_humidity_2m_mean", [])

        n = min(len(dates), len(tmean), len(prcp), len(rh))
        for i in range(n):
            rows.append([
                m.nome,
                dates[i],
                round(tmean[i], 2) if tmean[i] is not None else None,
                round(prcp[i], 2) if prcp[i] is not None else None,
                round(rh[i], 2) if rh[i] is not None else None,
            ])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"✅ Clima salvo: {OUTPUT_FILE}")
    print(f"📦 Registros: {len(rows):,}")


if __name__ == "__main__":
    main()


