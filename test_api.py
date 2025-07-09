#!/usr/bin/env python3
"""
Script para testar se a API do Facebook Ads Scraper está funcionando
"""

import requests
import time
import json

def test_api():
    """Testa se a API está respondendo"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testando API do Facebook Ads Scraper ===\n")
    
    # Aguardar um pouco para o servidor inicializar
    print("Aguardando servidor inicializar...")
    time.sleep(2)
    
    try:
        # Teste da página inicial
        print("1. Testando página inicial...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✓ Página inicial funcionando")
        else:
            print(f"✗ Página inicial com erro: {response.status_code}")
            
        # Teste do endpoint de health
        print("\n2. Testando endpoint de health...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✓ Endpoint de health funcionando")
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Timestamp: {data.get('timestamp', 'unknown')}")
        else:
            print(f"✗ Endpoint de health com erro: {response.status_code}")
            
        # Teste do endpoint has-ads
        print("\n3. Testando endpoint /api/has-ads...")
        payload = {"maps_address": "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ"}
        response = requests.post(f"{base_url}/api/has-ads", json=payload, timeout=30)
        if response.status_code == 200:
            print("✓ Endpoint /api/has-ads funcionando")
            data = response.json()
            print(f"  Resposta: {json.dumps(data, indent=2)}")
        else:
            print(f"✗ Endpoint /api/has-ads com erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Não foi possível conectar ao servidor")
        print("Verifique se o servidor está rodando: venv\\Scripts\\python.exe facebook_ads_scraper.py")
    except requests.exceptions.Timeout:
        print("✗ Timeout ao conectar ao servidor")
    except Exception as e:
        print(f"✗ Erro ao testar API: {e}")
    
    print("\n=== URLs Disponíveis ===")
    print("- http://127.0.0.1:5000 (Interface principal)")
    print("- http://127.0.0.1:5000/api/health (Health check)")
    print("- http://127.0.0.1:5000/api/has-ads (Verificação rápida de anúncios)")
    print("- http://127.0.0.1:5000/api/check-establishment (Verificação detalhada)")
    print("- http://127.0.0.1:5000/api/search-ads (Busca de anúncios)")
    print("- http://192.168.3.100:5000 (Acesso pela rede local)")
    
    print("\n=== Endpoints API ===")
    print("- POST /api/analyze-competition")
    print("- POST /api/check-advertiser")
    print("- POST /api/search-ads")
    print("- GET /api/health")
    print("- POST /api/has-ads")

if __name__ == "__main__":
    test_api()
