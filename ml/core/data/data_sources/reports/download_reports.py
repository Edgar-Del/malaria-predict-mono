#!/usr/bin/env python3
"""
Baixa relatórios públicos (PDF/Excel) para data/raw/reports a partir de uma lista de URLs.

Uso:
  python3 ml/data_sources/reports/download_reports.py [--urls ml/data_sources/reports/urls.txt]
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Iterable

import requests
from loguru import logger


DEFAULT_URLS_FILE = Path(__file__).with_name("urls.txt")
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "reports"


def read_urls(path: Path) -> Iterable[str]:
    if not path.exists():
        logger.error(f"Arquivo de URLs não encontrado: {path}")
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line


def download_file(url: str, out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    local_name = url.split("?")[0].split("/")[-1] or f"report_{int(time.time()*1000)}"
    dest = out_dir / local_name
    try:
        logger.info(f"Baixando: {url}")
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        logger.success(f"Salvo: {dest}")
        return dest
    except Exception as e:
        logger.error(f"Falha ao baixar {url}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", type=str, default=str(DEFAULT_URLS_FILE), help="Arquivo com URLs (um por linha)")
    args = parser.parse_args()

    urls_file = Path(args.urls)
    urls = list(read_urls(urls_file))
    logger.info(f"Total de URLs: {len(urls)}")

    downloaded = []
    for u in urls:
        dest = download_file(u, OUTPUT_DIR)
        if dest:
            downloaded.append(dest)

    logger.info(f"Concluído. Arquivos baixados: {len(downloaded)} em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()


