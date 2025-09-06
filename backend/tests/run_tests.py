"""
Script para executar todos os testes do projeto.
"""

import pytest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Executa todos os testes do projeto."""
    print("🧪 Executando testes do Sistema de Previsão de Risco de Malária - Bié")
    print("=" * 70)
    
    # Configurações do pytest
    pytest_args = [
        "tests/",
        "-v",  # Verbose
        "--tb=short",  # Traceback curto
        "--strict-markers",  # Marcadores estritos
        "--disable-warnings",  # Desabilitar warnings
        "--color=yes",  # Cores
        "-x",  # Parar no primeiro erro
    ]
    
    # Executar testes
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n✅ Todos os testes passaram com sucesso!")
    else:
        print(f"\n❌ Alguns testes falharam (código de saída: {exit_code})")
    
    return exit_code

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

