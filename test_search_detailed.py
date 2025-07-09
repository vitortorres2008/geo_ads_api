#!/usr/bin/env python3
"""
Script para testar especificamente o endpoint de busca de anúncios
"""

import requests
import json
import time

def test_search_ads():
    """Testa o endpoint de busca de anúncios"""
    url = "http://127.0.0.1:5000/api/search-ads"
    
    # Payload de teste
    payload = {
        "location": "São Paulo",
        "business_type": "academia",
        "max_results": 10
    }
    
    print("=== Testando Search Ads Endpoint ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        print("Enviando requisição...")
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== Resposta ===")
            print(f"Total encontrado: {data.get('total_found', 0)}")
            print(f"Localização: {data.get('location', 'N/A')}")
            print(f"Tipo de negócio: {data.get('business_type', 'N/A')}")
            
            ads = data.get('ads', [])
            print(f"\nAnúncios retornados: {len(ads)}")
            
            if ads:
                print("\n=== Primeiros anúncios ===")
                for i, ad in enumerate(ads[:3]):
                    print(f"\nAnúncio {i+1}:")
                    print(f"  Anunciante: {ad.get('advertiser_name', 'N/A')}")
                    print(f"  Texto: {ad.get('ad_text', 'N/A')[:100]}...")
                    print(f"  Imagens: {len(ad.get('image_urls', []))}")
                    if ad.get('debug_info'):
                        print(f"  Debug: {ad.get('debug_info')}")
            else:
                print("\n❌ Nenhum anúncio foi retornado")
                print("\nPossíveis causas:")
                print("1. Seletores CSS desatualizados")
                print("2. Facebook detectou automação")
                print("3. Página não carregou corretamente")
                print("4. Erro nos critérios de busca")
        else:
            print(f"\n❌ Erro HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Erro: {error_data.get('error', 'Erro desconhecido')}")
            except:
                print(f"Resposta: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Timeout - A requisição demorou mais de 60 segundos")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Verifique se o servidor está rodando")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_with_different_params():
    """Testa com diferentes parâmetros"""
    test_cases = [
        {"location": "Brasil", "business_type": "fitness"},
        {"location": "Rio de Janeiro", "business_type": "restaurante"},
        {"location": "São Paulo", "business_type": "loja"},
    ]
    
    print("\n=== Testando com Diferentes Parâmetros ===")
    
    for i, params in enumerate(test_cases):
        print(f"\nTeste {i+1}: {params}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/search-ads", 
                json=params, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_found', 0)
                print(f"  ✓ Sucesso: {total} anúncios encontrados")
            else:
                print(f"  ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(2)  # Delay entre testes

if __name__ == "__main__":
    test_search_ads()
    test_with_different_params()
