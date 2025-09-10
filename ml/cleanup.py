#!/usr/bin/env python3
"""
Script de limpeza final do diretório ML
Remove arquivos desnecessários e organiza estrutura
"""

import os
import shutil
from pathlib import Path

def cleanup_directory():
    """Limpa o diretório ML removendo arquivos desnecessários"""
    
    # Arquivos para remover
    files_to_remove = [
        'Dockerfile',
        'Makefile', 
        'pyproject.toml',
        'cleanup.py'  # Remove este próprio script
    ]
    
    # Diretórios para remover
    dirs_to_remove = [
        'data'  # Diretório vazio
    ]
    
    print("🧹 Iniciando limpeza do diretório ML...")
    
    # Remover arquivos
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removido: {file}")
    
    # Remover diretórios
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            if not os.listdir(dir_name):  # Se estiver vazio
                os.rmdir(dir_name)
                print(f"✅ Removido diretório vazio: {dir_name}")
    
    print("🎉 Limpeza concluída!")

def show_final_structure():
    """Mostra a estrutura final do diretório"""
    
    print("\n📁 ESTRUTURA FINAL DO DIRETÓRIO ML:")
    print("=" * 50)
    
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        items = sorted(Path(path).iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print_tree(".")

if __name__ == "__main__":
    cleanup_directory()
    show_final_structure()
