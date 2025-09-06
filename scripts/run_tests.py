#!/usr/bin/env python3
"""
Script para executar todos os testes do projeto.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.run_tests import run_tests

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

