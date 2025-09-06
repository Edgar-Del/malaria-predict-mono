#!/usr/bin/env python3
"""
Script para verificar a estrutura do projeto reorganizado.
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Verifica se a estrutura do projeto está completa."""
    
    print("🔍 Verificando estrutura do projeto...")
    print("=" * 50)
    
    # Estrutura esperada
    expected_structure = {
        "backend/": {
            "api/": ["main.py", "models.py", "routes.py"],
            "core/": ["__init__.py"],
            "infrastructure/": ["database_manager.py", "email_alerts.py", "worker.py"],
            "shared/": ["__init__.py"],
            "tests/": ["conftest.py"],
            "requirements.txt": True,
            "Dockerfile": True,
            "Makefile": True,
            "README.md": True,
        },
        "frontend/": {
            "web/": ["app/", "components/", "lib/"],
            "components/": [],
            "services/": [],
            "utils/": [],
            "package.json": True,
            "Dockerfile": True,
            "Makefile": True,
            "README.md": True,
        },
        "ml/": {
            "data/": ["__init__.py"],
            "features/": ["feature_engineering.py", "__init__.py"],
            "models/": ["trainer.py", "predictor.py", "__init__.py"],
            "training/": ["__init__.py"],
            "serving/": ["__init__.py"],
            "requirements.txt": True,
            "Dockerfile": True,
            "Makefile": True,
            "README.md": True,
        },
        "data/": {
            "raw/": [],
            "processed/": [],
            "external/": [],
        },
        "docs/": {
            "api/": [],
            "user/": [],
            "technical/": [],
        },
        "scripts/": ["check_system.py", "quick_start.sh", "setup_database.py"],
        "docker-compose.yml": True,
        "Makefile": True,
        "README.md": True,
        "env.example": True,
    }
    
    missing_files = []
    missing_dirs = []
    
    def check_path(path, expected, base_path=""):
        """Verifica se um caminho existe e tem os arquivos esperados."""
        full_path = Path(base_path) / path
        current_path = str(full_path)
        
        if not full_path.exists():
            if isinstance(expected, bool) and expected:
                missing_files.append(current_path)
            else:
                missing_dirs.append(current_path)
            return
        
        if isinstance(expected, dict):
            for item, sub_expected in expected.items():
                check_path(item, sub_expected, current_path)
        elif isinstance(expected, list):
            for item in expected:
                item_path = full_path / item
                if not item_path.exists():
                    missing_files.append(str(item_path))
    
    # Verificar estrutura
    for path, expected in expected_structure.items():
        check_path(path, expected)
    
    # Relatório
    print("\n📊 RELATÓRIO DE VERIFICAÇÃO:")
    print("-" * 30)
    
    if missing_dirs:
        print(f"❌ Diretórios faltando ({len(missing_dirs)}):")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
    else:
        print("✅ Todos os diretórios estão presentes")
    
    if missing_files:
        print(f"\n❌ Arquivos faltando ({len(missing_files)}):")
        for file_path in missing_files:
            print(f"   - {file_path}")
    else:
        print("\n✅ Todos os arquivos estão presentes")
    
    # Verificar arquivos importantes
    print("\n🔧 VERIFICAÇÃO DE ARQUIVOS IMPORTANTES:")
    print("-" * 40)
    
    important_files = [
        "docker-compose.yml",
        "Makefile",
        "README.md",
        "backend/api/main.py",
        "frontend/web/app/page.tsx",
        "ml/models/trainer.py",
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # Verificar permissões de scripts
    print("\n🔐 VERIFICAÇÃO DE PERMISSÕES:")
    print("-" * 30)
    
    scripts = [
        "scripts/quick_start.sh",
        "scripts/check_system.py",
        "scripts/setup_database.py",
    ]
    
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"✅ {script} (executável)")
            else:
                print(f"⚠️  {script} (não executável)")
        else:
            print(f"❌ {script} (não encontrado)")
    
    # Resumo final
    total_missing = len(missing_dirs) + len(missing_files)
    
    print("\n" + "=" * 50)
    if total_missing == 0:
        print("🎉 ESTRUTURA COMPLETA! O projeto está bem organizado.")
        return True
    else:
        print(f"⚠️  ESTRUTURA INCOMPLETA: {total_missing} itens faltando.")
        return False

if __name__ == "__main__":
    success = check_structure()
    sys.exit(0 if success else 1)
