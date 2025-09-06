#!/usr/bin/env python3
"""
Script para verificar o status do sistema de previsão de malária.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_api():
    """Verifica se a API está funcionando."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"API Online - Status: {data.get('status', 'unknown')}"
        else:
            return False, f"API retornou status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Erro ao conectar com API: {e}"

def check_dashboard():
    """Verifica se o dashboard está funcionando."""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            return True, "Dashboard Online"
        else:
            return False, f"Dashboard retornou status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Erro ao conectar com dashboard: {e}"

def check_database():
    """Verifica se o banco de dados está funcionando."""
    try:
        from src.ingest.database_manager import DatabaseManager
        db = DatabaseManager()
        if db.test_connection():
            return True, "Banco de Dados Online"
        else:
            return False, "Erro na conexão com banco de dados"
    except Exception as e:
        return False, f"Erro ao verificar banco: {e}"

def check_model():
    """Verifica se o modelo está carregado."""
    try:
        from src.model.predictor import ModelPredictor
        predictor = ModelPredictor()
        if predictor.is_model_loaded():
            info = predictor.get_model_info()
            return True, f"Modelo Online - Versão: {info.get('model_version', 'unknown')}"
        else:
            return False, "Modelo não carregado"
    except Exception as e:
        return False, f"Erro ao verificar modelo: {e}"

def main():
    """Função principal."""
    print("🔍 Verificação do Sistema de Previsão de Malária - Bié")
    print("=" * 60)
    
    checks = [
        ("API", check_api),
        ("Dashboard", check_dashboard),
        ("Banco de Dados", check_database),
        ("Modelo ML", check_model)
    ]
    
    all_ok = True
    
    for name, check_func in checks:
        print(f"\n📊 Verificando {name}...")
        try:
            success, message = check_func()
            if success:
                print(f"  ✅ {message}")
            else:
                print(f"  ❌ {message}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ Erro inesperado: {e}")
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 Sistema funcionando perfeitamente!")
        print("\n📍 Acesse os serviços:")
        print("  🌐 Dashboard: http://localhost:3000")
        print("  🔌 API: http://localhost:8000")
        print("  📚 Documentação: http://localhost:8000/docs")
    else:
        print("⚠️  Alguns serviços não estão funcionando corretamente.")
        print("   Verifique os logs com: docker-compose logs -f")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

