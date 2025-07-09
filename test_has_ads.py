#!/usr/bin/env python3
"""
Script para testar o endpoint /api/has-ads
Teste rápido que retorna apenas has_ads: boolean
"""

import requests
import json

def test_has_ads():
    """Testa o endpoint /api/has-ads"""
    
    url = "http://127.0.0.1:5000/api/has-ads"
    
    # Teste 1: Estabelecimento conhecido com anúncios
    test_cases = [
        {
            "name": "Balada Mix RJ - deve ter anúncios",
            "maps_address": "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ"
        },
        {
            "name": "Shopping Iguatemi SP - pode ter anúncios",
            "maps_address": "Shopping Iguatemi - Av. Brigadeiro Faria Lima, 2232 - Jardim Paulistano, São Paulo - SP"
        },
        {
            "name": "Endereço fictício - não deve ter anúncios",
            "maps_address": "Loja XYZ123 - Rua Inexistente, 999 - Bairro Fictício, Cidade Imaginária"
        }
    ]
    
    print("🔍 Testando endpoint /api/has-ads")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: {test_case['name']}")
        print(f"Endereço: {test_case['maps_address']}")
        
        payload = {"maps_address": test_case['maps_address']}
        
        try:
            print("Enviando requisição...")
            response = requests.post(url, json=payload, timeout=60)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                has_ads = result.get('has_ads', False)
                
                print(f"✅ Resposta: {json.dumps(result, indent=2)}")
                print(f"📊 Resultado: {'TEM ANÚNCIOS' if has_ads else 'SEM ANÚNCIOS'}")
                
            else:
                print(f"❌ Erro: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - requisição demorou mais que 60 segundos")
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
        
        print("-" * 30)

def test_invalid_requests():
    """Testa requisições inválidas"""
    
    url = "http://127.0.0.1:5000/api/has-ads"
    
    print("\n🚫 Testando requisições inválidas")
    print("=" * 50)
    
    # Teste sem maps_address
    print("Teste: Requisição sem maps_address")
    try:
        response = requests.post(url, json={}, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"Erro: {str(e)}")
    
    print("-" * 30)
    
    # Teste com maps_address vazio
    print("Teste: Requisição com maps_address vazio")
    try:
        response = requests.post(url, json={"maps_address": ""}, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do endpoint /api/has-ads")
    print("Certifique-se de que a API está rodando em http://127.0.0.1:5000")
    
    # Testa se a API está disponível
    try:
        health_response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ API está rodando")
            test_has_ads()
            test_invalid_requests()
        else:
            print("❌ API não está respondendo corretamente")
    except Exception as e:
        print(f"❌ Não foi possível conectar à API: {str(e)}")
        print("Execute: python facebook_ads_scraper.py")
