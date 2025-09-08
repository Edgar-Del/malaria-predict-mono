#!/usr/bin/env python3
"""
Extrai tabelas relevantes de relatórios (PDF/Excel) em data/raw/reports e
gera data/raw/casos_bie.csv no formato esperado pelo pipeline.

Suporta:
- PDF (tabelas simples) via pdfplumber
- Excel (.xlsx) via openpyxl

Formato de saída:
  municipio,data,casos_confirmados

Observação: Os relatórios públicos variam. Este script implementa heurísticas e
mapas de nomes de municípios para o Bié; pode ser necessário ajustar regras.
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pdfplumber
import openpyxl
from loguru import logger
import pandas as pd


REPORTS_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "reports"
OUTPUT_FILE = Path(__file__).resolve().parents[2] / "data" / "raw" / "casos_bie.csv"


MUNICIPIOS_BIE = {
    "Kuito": "Kuito",
    "Cuito": "Kuito",
    "Andulo": "Andulo",
    "Camacupa": "Camacupa",
    "Catabola": "Catabola",
    "Chinguar": "Chinguar",
    "Chitembo": "Chitembo",
    "Cuemba": "Cuemba",
    "Cunhinga": "Cunhinga",
    "Nharea": "Nharea",
    "Nharéa": "Nharea",
}


def parse_excel(path: Path) -> List[Dict[str, str]]:
    wb = openpyxl.load_workbook(path, data_only=True)
    rows = []
    for ws in wb.worksheets:
        headers: Dict[int, str] = {}
        for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            values = ["" if v is None else str(v).strip() for v in row]
            if r_idx == 1:
                for c_idx, v in enumerate(values):
                    headers[c_idx] = v.lower()
                continue
            record = {headers.get(i, f"col{i}"): v for i, v in enumerate(values)}
            rows.append(record)
    return rows


def parse_pdf(path: Path) -> List[List[str]]:
    data: List[List[str]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for t in tables or []:
                for row in t:
                    if row and any(cell for cell in row):
                        data.append(["" if c is None else str(c).strip() for c in row])
    return data


def parse_csv(path: Path) -> List[Dict[str, str]]:
    """Lê CSVs diversos e tenta padronizar colunas.

    Estratégias suportadas:
      1) CSV já no formato esperado (municipio, data, casos_confirmados)
      2) CSV país/ano (ex.: WHO/OWID/WorldBank) -> gera linha com municipio="Angola"
    """
    rows: List[Dict[str, str]] = []
    try:
        df = pd.read_csv(path)
    except Exception as e:
        logger.error(f"Falha ao ler CSV {path.name}: {e}")
        return rows

    # Caso 1: já no formato esperado
    lower_cols = {c.lower(): c for c in df.columns}
    if {"municipio", "data", "casos_confirmados"}.issubset(set(lower_cols.keys())):
        for _, r in df.iterrows():
            rows.append({
                "municipio": str(r[lower_cols["municipio"]]).strip(),
                "data": str(r[lower_cols["data"]]).strip(),
                "casos_confirmados": str(r[lower_cols["casos_confirmados"]]).strip(),
            })
        return rows

    # Caso 2: país/ano (e.g., Entity/Year/Malaria cases) -> Angola
    candidates_entity = [c for c in df.columns if str(c).lower() in ("entity", "country", "location", "pais")]
    candidates_year = [c for c in df.columns if str(c).lower() in ("year", "ano")]
    candidates_value = [c for c in df.columns if "malaria" in str(c).lower() or str(c).lower() in ("cases", "value", "val")]

    if candidates_entity and candidates_year and candidates_value:
        ent_col = candidates_entity[0]
        year_col = candidates_year[0]
        val_col = candidates_value[0]
        sub = df[df[ent_col].astype(str).str.strip().str.lower().isin(["angola"])].copy()
        if not sub.empty:
            for _, r in sub.iterrows():
                try:
                    year = int(str(r[year_col]).split(".")[0])
                    d_iso = f"{year}-12-31"
                    val = int(float(r[val_col]))
                except Exception:
                    continue
                rows.append({
                    "municipio": "Angola",
                    "data": d_iso,
                    "casos_confirmados": str(val),
                })
            if rows:
                logger.warning(
                    f"{path.name}: CSV em nível nacional convertido para municipio='Angola' (sem granularidade municipal)."
                )
                return rows

    logger.warning(f"{path.name}: CSV ignorado (colunas não reconhecidas para extração de casos).")
    return rows


def normalize_row_to_cases(row: Dict[str, str]) -> Optional[Dict[str, str]]:
    # Heurísticas comuns
    municipio = None
    for key in ("municipio", "município", "municipality", "munic", "prov_munic"):
        if key in row:
            municipio = row[key]
            break
    if municipio is None:
        return None
    municipio = MUNICIPIOS_BIE.get(municipio.strip(), None)
    if municipio is None:
        return None

    data_str = None
    for key in ("data", "date", "dt", "week_start", "semana_inicio"):
        if key in row:
            data_str = row[key]
            break
    if not data_str:
        return None
    # Tentar múltiplos formatos
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            d = datetime.strptime(data_str[:10], fmt).date()
            data_iso = d.isoformat()
            break
        except Exception:
            data_iso = None
    if not data_iso:
        return None

    casos = None
    for key in ("casos", "casos_confirmados", "cases", "confirmed"):
        if key in row:
            try:
                casos = int(float(row[key].replace(",", ".")))
            except Exception:
                pass
            break
    if casos is None:
        return None

    return {"municipio": municipio, "data": data_iso, "casos_confirmados": str(casos)}


def process_reports() -> int:
    if not REPORTS_DIR.exists():
        logger.error(f"Diretório de relatórios não existe: {REPORTS_DIR}")
        return 0

    out_rows: List[Dict[str, str]] = []
    for path in sorted(REPORTS_DIR.iterdir()):
        if path.suffix.lower() in {".xlsx", ".xlsm"}:
            rows = parse_excel(path)
            for r in rows:
                norm = normalize_row_to_cases(r)
                if norm:
                    out_rows.append(norm)
        elif path.suffix.lower() == ".csv":
            csv_rows = parse_csv(path)
            for r in csv_rows:
                norm = normalize_row_to_cases(r)
                # Se já está no formato final (municipio/data/casos), normalize_row_to_cases retornará igual
                if norm:
                    out_rows.append(norm)
                else:
                    # Caso seja registro nacional (municipio='Angola'), aceitar diretamente
                    if {"municipio", "data", "casos_confirmados"}.issubset(set(r.keys())):
                        out_rows.append(r)
        elif path.suffix.lower() == ".pdf":
            tables = parse_pdf(path)
            # Converter listas em dicts heurísticos (precisa de adaptação por relatório)
            for row in tables:
                if len(row) < 3:
                    continue
                guess = {"municipio": row[0], "data": row[1], "casos": row[2]}
                norm = normalize_row_to_cases(guess)
                if norm:
                    out_rows.append(norm)

    if not out_rows:
        logger.warning("Nenhum dado extraído. Verifique os relatórios e heurísticas.")
        return 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["municipio", "data", "casos_confirmados"])
        w.writeheader()
        w.writerows(out_rows)

    logger.success(f"Salvo: {OUTPUT_FILE} ({len(out_rows)} linhas)")
    return len(out_rows)


def main():
    total = process_reports()
    print(f"Linhas extraídas: {total}")


if __name__ == "__main__":
    main()


