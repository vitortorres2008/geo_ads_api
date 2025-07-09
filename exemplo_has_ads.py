#!/usr/bin/env python3
"""
Exemplo simples de uso do endpoint /api/has-ads
Este endpoint retorna apenas {"has_ads": boolean} para verificações rápidas
"""

import requests
import json

def check_if_has_ads(maps_address):
    """Verifica se um estabelecimento tem anúncios - retorna apenas boolean"""
    
    url = "http://127.0.0.1:5000/api/has-ads"
    payload = {"maps_address": maps_address}
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('has_ads', False)
        else:
            print(f"Erro na requisição: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Erro: {str(e)}")
        return False

# Exemplos de uso
if __name__ == "__main__":
    print("🔍 Verificador Rápido de Anúncios")
    print("=" * 40)
    
    # Lista de estabelecimentos para testar
    estabelecimentos = [
        "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ",
        "Shopping Iguatemi - Av. Brigadeiro Faria Lima, 2232 - Jardim Paulistano, São Paulo - SP",
        "McDonald's - Av. Paulista, 1230 - Bela Vista, São Paulo - SP"
    ]
    
    for endereco in estabelecimentos:
        print(f"\n📍 Verificando: {endereco[:50]}...")
        
        has_ads = check_if_has_ads(endereco)
        
        if has_ads:
            print("✅ TEM ANÚNCIOS")
        else:
            print("❌ SEM ANÚNCIOS")
    
    print("\n" + "=" * 40)
    print("✨ Verificação concluída!")
