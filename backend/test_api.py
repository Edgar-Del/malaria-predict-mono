#!/usr/bin/env python3
"""
Script de teste para a API do backend.
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

def test_api():
    """Testa a API do backend."""
    
    print("🧪 Testando API do Backend...")
    print("=" * 50)
    
    # URL base da API
    base_url = "http://localhost:8000"
    
    # Teste 1: Health Check
    print("\n1. Testando Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check OK: {data}")
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # Teste 2: Informações do modelo
    print("\n2. Testando informações do modelo...")
    try:
        response = requests.get(f"{base_url}/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modelo info OK: {data}")
        else:
            print(f"❌ Modelo info falhou: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na conexão: {e}")
    
    # Teste 3: Lista de municípios
    print("\n3. Testando lista de municípios...")
    try:
        response = requests.get(f"{base_url}/municipios", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Municípios OK: {len(data.get('municipios', []))} municípios encontrados")
        else:
            print(f"❌ Municípios falhou: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na conexão: {e}")
    
    # Teste 4: Previsão de risco
    print("\n4. Testando previsão de risco...")
    try:
        prediction_data = {
            "municipio": "Cuito",
            "ano_semana": "2024-52"
        }
        response = requests.post(
            f"{base_url}/predict", 
            json=prediction_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Previsão OK: {data}")
        else:
            print(f"❌ Previsão falhou: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na conexão: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    return True

def start_api_server():
    """Inicia o servidor da API em background."""
    print("🚀 Iniciando servidor da API...")
    
    try:
        # Iniciar servidor em background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para o servidor inicializar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def main():
    """Função principal."""
    print("🔧 Sistema de Teste da API - Backend")
    print("=" * 50)
    
    # Iniciar servidor
    server_process = start_api_server()
    
    if server_process is None:
        print("❌ Não foi possível iniciar o servidor")
        return
    
    try:
        # Executar testes
        test_api()
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
    
    finally:
        # Parar servidor
        if server_process:
            print("\n🛑 Parando servidor...")
            server_process.terminate()
            server_process.wait()
            print("✅ Servidor parado")

if __name__ == "__main__":
    main()


