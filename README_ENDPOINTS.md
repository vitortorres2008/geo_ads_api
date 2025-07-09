# Facebook Ads API - Endpoints Disponíveis

## 🚀 Visão Geral

Esta API permite verificar se estabelecimentos possuem anúncios ativos na biblioteca de anúncios do Facebook.

## 📋 Endpoints Principais

### 1. `/api/has-ads` (POST) - ⚡ Verificação Rápida

**Uso:** Verificação simples e rápida se um estabelecimento tem anúncios.

**Payload:**
```json
{
    "maps_address": "Nome do Estabelecimento - Endereço completo"
}
```

**Resposta:**
```json
{
    "has_ads": true
}
```

**Exemplo com cURL:**
```bash
curl -X POST http://127.0.0.1:5000/api/has-ads \
  -H "Content-Type: application/json" \
  -d '{"maps_address": "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ"}'
```

### 2. `/api/check-establishment` (POST) - 📊 Verificação Detalhada

**Uso:** Verificação completa com detalhes dos anúncios encontrados.

**Payload:**
```json
{
    "maps_address": "Nome do Estabelecimento - Endereço completo"
}
```

**Resposta:**
```json
{
    "has_ads": true,
    "confidence": 85,
    "establishment_name": "Balada Mix",
    "ads_found": 3,
    "ads": [
        {
            "advertiser_name": "Balada Mix",
            "ad_text": "A melhor balada do Rio!",
            "images": ["url1", "url2"],
            "links": ["https://..."],
            "ad_id": "123456"
        }
    ]
}
```

### 3. `/api/search-ads` (POST) - 🔍 Busca Personalizada

**Payload:**
```json
{
    "keywords": "academia",
    "location": "Brazil",
    "business_type": "fitness"
}
```

### 4. `/api/health` (GET) - ✅ Status da API

**Resposta:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

## 🛠️ Como Usar

### Iniciando a API
```bash
cd c:\projetos\prospect-api
python facebook_ads_scraper.py
```

### Testando os Endpoints
```bash
# Teste rápido
python test_has_ads.py

# Teste geral
python test_api.py

# Comparação de endpoints
python compare_endpoints.py

# Exemplo simples
python exemplo_has_ads.py
```

## 📝 Quando Usar Cada Endpoint

| Endpoint | Quando Usar | Resposta | Velocidade |
|----------|-------------|----------|------------|
| `/api/has-ads` | Verificação simples, dashboard, automação | Apenas boolean | ⚡ Mais rápida |
| `/api/check-establishment` | Análise detalhada, relatórios | Dados completos | 🔍 Mais detalhada |
| `/api/search-ads` | Pesquisa personalizada por critérios | Lista de anúncios | 🔍 Busca ampla |

## 🔧 Exemplos de Integração

### Python
```python
import requests

# Verificação rápida
def tem_anuncios(endereco):
    response = requests.post(
        "http://127.0.0.1:5000/api/has-ads",
        json={"maps_address": endereco}
    )
    return response.json().get('has_ads', False)

# Uso
if tem_anuncios("McDonald's - Av. Paulista, 1230 - São Paulo"):
    print("Estabelecimento anuncia no Facebook!")
```

### JavaScript
```javascript
async function hasAds(mapsAddress) {
    const response = await fetch('http://127.0.0.1:5000/api/has-ads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ maps_address: mapsAddress })
    });
    
    const result = await response.json();
    return result.has_ads;
}
```

## 🎯 Casos de Uso

- **Análise de Concorrência:** Verificar se concorrentes estão anunciando
- **Prospecção de Clientes:** Identificar empresas que já usam Facebook Ads
- **Monitoramento:** Acompanhar status de anúncios de estabelecimentos
- **Automação:** Integrar em sistemas de CRM ou dashboards

## 📊 Interface Web

Acesse `http://127.0.0.1:5000` para ver a interface web com documentação completa e exemplos interativos.
