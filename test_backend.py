#!/usr/bin/env python3
"""
Script para testar o backend localmente
"""
import subprocess
import sys
import os

def test_backend():
    print("🔧 Testando Backend...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("backend/requirements.txt"):
        print("❌ Diretório backend não encontrado")
        return False
    
    # Testar instalação das dependências
    print("📦 Testando instalação de dependências...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso")
        else:
            print(f"❌ Erro na instalação: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout na instalação das dependências")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    print("✅ Backend testado com sucesso!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
