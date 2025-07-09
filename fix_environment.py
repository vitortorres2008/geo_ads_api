#!/usr/bin/env python3
"""
Script para corrigir o ambiente virtual e dependências
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"Executando: {description}")
    print(f"Comando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ Sucesso: {description}")
        if result.stdout:
            print(f"Saída: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro: {description}")
        print(f"Código de saída: {e.returncode}")
        if e.stdout:
            print(f"Saída: {e.stdout}")
        if e.stderr:
            print(f"Erro: {e.stderr}")
        return False

def main():
    print("=== Corrigindo Ambiente Virtual ===\n")
    
    # Verificar se está no ambiente virtual
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Ambiente virtual detectado")
    else:
        print("✗ Ambiente virtual não detectado")
        print("Ative o ambiente virtual primeiro: venv\\Scripts\\activate")
        return
    
    # Atualizar pip
    run_command(f'"{sys.executable}" -m pip install --upgrade pip', "Atualizando pip")
    
    # Desinstalar pandas e numpy se existirem
    run_command(f'"{sys.executable}" -m pip uninstall pandas numpy -y', "Desinstalando pandas e numpy")
    
    # Instalar numpy primeiro
    run_command(f'"{sys.executable}" -m pip install numpy==1.24.3', "Instalando numpy")
    
    # Instalar pandas
    run_command(f'"{sys.executable}" -m pip install pandas==2.1.1', "Instalando pandas")
    
    # Instalar outras dependências
    dependencies = [
        'selenium==4.15.2',
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'flask==2.3.3',
        'flask-cors==4.0.0',
        'webdriver-manager==4.0.1'
    ]
    
    for dep in dependencies:
        run_command(f'"{sys.executable}" -m pip install {dep}', f"Instalando {dep}")
    
    # Testar importações
    print("\n=== Testando Importações ===")
    test_imports = [
        'import numpy',
        'import pandas',
        'import selenium',
        'import flask',
        'import requests',
        'import bs4'
    ]
    
    for import_test in test_imports:
        try:
            exec(import_test)
            print(f"✓ {import_test}")
        except Exception as e:
            print(f"✗ {import_test}: {e}")
    
    print("\n=== Configuração Concluída ===")

if __name__ == "__main__":
    main()
