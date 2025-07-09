#!/usr/bin/env python3
"""
Script para testar o endpoint de verificação de estabelecimentos
"""

import requests
import json
import time

def test_establishment_check():
    """Testa o endpoint de verificação de estabelecimentos"""
    url = "http://127.0.0.1:5000/api/check-establishment"
    
    # Casos de teste
    test_cases = [
        {
            "name": "Balada Mix RJ (que sabemos que tem anúncios)",
            "maps_address": "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ"
        },
        {
            "name": "McDonald's Copacabana",
            "maps_address": "McDonald's - Av. Nossa Senhora de Copacabana, 1226 - Copacabana, Rio de Janeiro - RJ"
        },
        {
            "name": "Restaurante qualquer",
            "maps_address": "Pizzaria do João - Rua das Flores, 123 - Ipanema, Rio de Janeiro - RJ"
        },
        {
            "name": "Academia de exemplo",
            "maps_address": "Smart Fit - Av. Rio Branco, 200 - Centro, Rio de Janeiro - RJ"
        }
    ]
    
    print("=== Testando Verificação de Estabelecimentos ===\n")
    
    for i, test_case in enumerate(test_cases):
        print(f"Teste {i+1}: {test_case['name']}")
        print(f"Endereço: {test_case['maps_address']}")
        print("-" * 60)
        
        try:
            payload = {"maps_address": test_case['maps_address']}
            
            print("Enviando requisição...")
            response = requests.post(url, json=payload, timeout=120)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Estabelecimento encontrado: {data.get('establishment_found', False)}")
                print(f"📱 Tem anúncios: {data.get('has_ads', False)}")
                print(f"🔢 Total anúncios correspondentes: {data.get('total_matching_ads', 0)}")
                print(f"🔍 Total anúncios pesquisados: {data.get('total_ads_searched', 0)}")
                
                # Informações do estabelecimento
                establishment_info = data.get('establishment_info', {})
                if establishment_info:
                    print(f"📍 Nome extraído: {establishment_info.get('name', 'N/A')}")
                    print(f"🏙️ Cidade: {establishment_info.get('city', 'N/A')}")
                    print(f"🏘️ Bairro: {establishment_info.get('neighborhood', 'N/A')}")
                    print(f"🏪 Categoria: {establishment_info.get('category', 'N/A')}")
                
                # Anúncios correspondentes
                matching_ads = data.get('matching_ads', [])
                if matching_ads:
                    print(f"\n📊 Anúncios encontrados:")
                    for j, ad in enumerate(matching_ads[:3]):
                        print(f"  {j+1}. {ad.get('advertiser_name', 'N/A')}")
                        print(f"     Confiança: {ad.get('match_confidence', 0):.2f}")
                        print(f"     Estratégia: {ad.get('match_strategy', 'N/A')}")
                        print(f"     Texto: {ad.get('ad_text', '')[:100]}...")
                        print()
                else:
                    print("❌ Nenhum anúncio correspondente encontrado")
                    
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Erro: {error_data.get('error', 'Erro desconhecido')}")
                except:
                    print(f"Resposta: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("❌ Timeout - A requisição demorou mais de 2 minutos")
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão - Verifique se o servidor está rodando")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # Delay entre testes
        if i < len(test_cases) - 1:
            time.sleep(5)

def test_simple_establishment():
    """Teste rápido com um estabelecimento conhecido"""
    url = "http://127.0.0.1:5000/api/check-establishment"
    
    payload = {
        "maps_address": "Balada Mix RJ - Copacabana, Rio de Janeiro"
    }
    
    print("=== Teste Rápido ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Resultado:")
            print(f"Tem anúncios: {data.get('has_ads', False)}")
            print(f"Total encontrados: {data.get('total_matching_ads', 0)}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1. Teste completo (4 estabelecimentos)")
    print("2. Teste rápido (1 estabelecimento)")
    
    try:
        choice = input("Digite 1 ou 2: ").strip()
        
        if choice == "1":
            test_establishment_check()
        elif choice == "2":
            test_simple_establishment()
        else:
            print("Opção inválida. Executando teste rápido...")
            test_simple_establishment()
            
    except KeyboardInterrupt:
        print("\nTeste cancelado pelo usuário.")
