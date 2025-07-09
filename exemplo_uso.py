from facebook_ads_scraper import FacebookAdsLibraryScraper, app
import json

def exemplo_uso_basico():
    """Exemplo básico de uso do scraper"""
    scraper = FacebookAdsLibraryScraper(headless=True)
    
    try:
        # Buscar anúncios de restaurantes em São Paulo
        print("Buscando anúncios de restaurantes em São Paulo...")
        ads = scraper.search_ads_by_location_and_type("São Paulo", "restaurante", max_results=20)
        
        print(f"Encontrados {len(ads)} anúncios")
        
        # Salvar em arquivo JSON
        with open('ads_sao_paulo_restaurantes.json', 'w', encoding='utf-8') as f:
            json.dump(ads, f, ensure_ascii=False, indent=2)
        
        # Analisar concorrência
        print("\nAnalisando concorrência...")
        analysis = scraper.analyze_competition("São Paulo", "restaurante")
        
        print(f"Nível de concorrência: {analysis['competition_level']}")
        print(f"Total de anúncios: {analysis['total_ads']}")
        print(f"Anunciantes ativos: {analysis['active_advertisers']}")
        
        # Verificar anunciante específico
        print("\nVerificando anunciante específico...")
        advertiser_info = scraper.get_advertiser_info("McDonald's")
        print(f"McDonald's tem anúncios ativos: {advertiser_info['has_active_ads']}")
        
    finally:
        scraper.close()

def exemplo_integracao_com_seu_sistema():
    """Exemplo de como integrar com seu sistema existente"""
    
    # Simulando dados que você já tem do Google Maps
    estabelecimentos_google = [
        {
            "name": "Restaurante Bella Vista",
            "address": "Rua das Flores, 123 - São Paulo, SP",
            "place_id": "ChIJN1t_tDeuhF8WSUPfJOKdgFD",
            "rating": 4.5,
            "types": ["restaurant", "food", "point_of_interest"]
        },
        {
            "name": "Padaria Pão Dourado",
            "address": "Av. Paulista, 456 - São Paulo, SP", 
            "place_id": "ChIJN1t_tDeuhF8WSUPfJOKdgFE",
            "rating": 4.2,
            "types": ["bakery", "food", "store"]
        }
    ]
    
    scraper = FacebookAdsLibraryScraper(headless=True)
    
    try:
        # Para cada estabelecimento, verificar se tem anúncios
        for estabelecimento in estabelecimentos_google:
            print(f"\nVerificando: {estabelecimento['name']}")
            
            # Buscar anúncios específicos do estabelecimento
            advertiser_info = scraper.get_advertiser_info(estabelecimento['name'])
            
            # Adicionar informação de anúncios aos dados existentes
            estabelecimento['meta_ads'] = {
                'has_ads': advertiser_info['has_active_ads'],
                'total_ads': advertiser_info['total_ads'],
                'prospecting_priority': 'baixa' if advertiser_info['has_active_ads'] else 'alta'
            }
            
            print(f"Tem anúncios: {advertiser_info['has_active_ads']}")
            print(f"Prioridade de prospecção: {estabelecimento['meta_ads']['prospecting_priority']}")
    
    finally:
        scraper.close()
    
    return estabelecimentos_google

def exemplo_api_calls():
    """Exemplo de como fazer chamadas para a API"""
    import requests
    
    base_url = "http://localhost:5000/api"
    
    # Analisar concorrência
    response = requests.post(f"{base_url}/analyze-competition", json={
        "location": "São Paulo",
        "business_type": "restaurante"
    })
    
    if response.status_code == 200:
        competition_data = response.json()
        print(f"Concorrência em SP - Restaurantes: {competition_data['competition_level']}")
    
    # Verificar anunciante específico
    response = requests.post(f"{base_url}/check-advertiser", json={
        "advertiser_name": "McDonald's"
    })
    
    if response.status_code == 200:
        advertiser_data = response.json()
        print(f"McDonald's tem anúncios: {advertiser_data['has_active_ads']}")
    
    # Buscar anúncios
    response = requests.post(f"{base_url}/search-ads", json={
        "location": "Rio de Janeiro",
        "business_type": "padaria",
        "max_results": 30
    })
    
    if response.status_code == 200:
        ads_data = response.json()
        print(f"Encontrados {ads_data['total_found']} anúncios de padarias no RJ")

if __name__ == "__main__":
    print("Executando exemplos de uso...")
    
    # Descomente a linha abaixo para testar
    # exemplo_uso_basico()
    
    # Para testar integração com seu sistema
    # exemplo_integracao_com_seu_sistema()
    
    print("Exemplos concluídos!")