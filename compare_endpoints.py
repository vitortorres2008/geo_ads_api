#!/usr/bin/env python3
"""
Comparação entre os endpoints /api/check-establishment e /api/has-ads
Mostra a diferença de resposta e uso de cada um
"""

import requests
import json
import time

def compare_endpoints(maps_address):
    """Compara os dois endpoints para o mesmo endereço"""
    
    base_url = "http://127.0.0.1:5000"
    
    print(f"🔍 Comparando endpoints para: {maps_address[:60]}...")
    print("=" * 80)
    
    # Teste do endpoint completo
    print("\n📊 ENDPOINT COMPLETO: /api/check-establishment")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/check-establishment",
            json={"maps_address": maps_address},
            timeout=60
        )
        
        end_time = time.time()
        duration_full = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"⏱️  Tempo: {duration_full:.2f}s")
            print(f"📈 Dados retornados:")
            print(f"   - has_ads: {result.get('has_ads', False)}")
            print(f"   - confidence: {result.get('confidence', 0)}")
            print(f"   - establishment_name: {result.get('establishment_name', 'N/A')}")
            print(f"   - ads_found: {result.get('ads_found', 0)}")
            print(f"   - Tamanho da resposta: {len(json.dumps(result))} caracteres")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"⏱️  Tempo: {duration_full:.2f}s")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Teste do endpoint simples
    print("\n⚡ ENDPOINT RÁPIDO: /api/has-ads")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/has-ads",
            json={"maps_address": maps_address},
            timeout=60
        )
        
        end_time = time.time()
        duration_simple = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"⏱️  Tempo: {duration_simple:.2f}s")
            print(f"📈 Dados retornados:")
            print(f"   - has_ads: {result.get('has_ads', False)}")
            print(f"   - Tamanho da resposta: {len(json.dumps(result))} caracteres")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"⏱️  Tempo: {duration_simple:.2f}s")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    print("\n" + "=" * 80)

def main():
    """Função principal"""
    
    print("🚀 COMPARAÇÃO DE ENDPOINTS - Facebook Ads API")
    print("Comparando /api/check-establishment vs /api/has-ads")
    
    # Verificar se a API está rodando
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API não está respondendo. Execute: python facebook_ads_scraper.py")
            return
    except:
        print("❌ API não está disponível. Execute: python facebook_ads_scraper.py")
        return
    
    # Endereços para teste
    enderecos = [
        "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ",
        "McDonald's - Av. Paulista, 1230 - Bela Vista, São Paulo - SP"
    ]
    
    for endereco in enderecos:
        compare_endpoints(endereco)
        print("\n" + "🔄" * 20 + "\n")
    
    print("📋 RESUMO:")
    print("- /api/check-establishment: Retorna dados completos (anúncios, confiança, etc)")
    print("- /api/has-ads: Retorna apenas boolean - ideal para verificações rápidas")
    print("- Ambos usam a mesma lógica de processamento internamente")

if __name__ == "__main__":
    main()
