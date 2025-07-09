#!/usr/bin/env python3
"""
Script simples para testar se as dependências estão funcionando
"""

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    import_tests = [
        ('numpy', 'import numpy as np'),
        ('pandas', 'import pandas as pd'),
        ('selenium', 'from selenium import webdriver'),
        ('flask', 'from flask import Flask'),
        ('requests', 'import requests'),
        ('beautifulsoup4', 'from bs4 import BeautifulSoup'),
        ('webdriver_manager', 'from webdriver_manager.chrome import ChromeDriverManager'),
        ('flask_cors', 'from flask_cors import CORS')
    ]
    
    print("=== Testando Importações ===")
    all_good = True
    
    for package, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"✓ {package}")
        except Exception as e:
            print(f"✗ {package}: {e}")
            all_good = False
    
    return all_good

def test_versions():
    """Testa as versões das dependências"""
    print("\n=== Versões das Dependências ===")
    
    try:
        import numpy
        print(f"NumPy: {numpy.__version__}")
    except:
        print("NumPy: Não instalado")
    
    try:
        import pandas
        print(f"Pandas: {pandas.__version__}")
    except:
        print("Pandas: Não instalado")
    
    try:
        import selenium
        print(f"Selenium: {selenium.__version__}")
    except:
        print("Selenium: Não instalado")
    
    try:
        import flask
        print(f"Flask: {flask.__version__}")
    except:
        print("Flask: Não instalado")

def main():
    print("=== Teste de Dependências ===\n")
    
    if test_imports():
        print("\n✓ Todas as dependências foram importadas com sucesso!")
        test_versions()
        print("\n✓ Ambiente está pronto para uso!")
    else:
        print("\n✗ Algumas dependências estão faltando ou com problema.")
        print("Execute: venv\\Scripts\\python.exe fix_environment.py")

if __name__ == "__main__":
    main()
