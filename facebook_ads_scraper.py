import requests
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import json
import urllib.parse
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookAdsLibraryScraper:
    def __init__(self, headless=True, use_proxy=False):
        self.base_url = "https://www.facebook.com/ads/library/"
        self.session = requests.Session()
        self.driver = None
        self.headless = headless
        self.use_proxy = use_proxy
        
        # Headers para parecer mais humano
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session.headers.update(self.headers)
    
    def setup_driver(self):
        """Configura o WebDriver do Selenium"""
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import os
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Opções para evitar detecção e melhorar estabilidade
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=pt-BR")
        
        # Configurações para melhor performance
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-gpu-logging")
        chrome_options.add_argument("--silent")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações de proxy se necessário
        if self.use_proxy:
            # Adicione suas configurações de proxy aqui
            pass
        
        try:
            # Instalar ChromeDriver com correção para Windows
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver baixado em: {driver_path}")
            
            # Corrigir o caminho do ChromeDriver no Windows
            if os.name == 'nt':  # Windows
                driver_dir = os.path.dirname(driver_path)
                # Procurar pelo executável real
                for file in os.listdir(driver_dir):
                    if file.endswith('.exe') and 'chromedriver' in file.lower():
                        driver_path = os.path.join(driver_dir, file)
                        break
                else:
                    # Se não encontrar, tentar na subpasta chromedriver-win32
                    win32_dir = os.path.join(driver_dir, 'chromedriver-win32')
                    if os.path.exists(win32_dir):
                        for file in os.listdir(win32_dir):
                            if file.endswith('.exe') and 'chromedriver' in file.lower():
                                driver_path = os.path.join(win32_dir, file)
                                break
            
            logger.info(f"ChromeDriver executável: {driver_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"ChromeDriver não encontrado em: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Scripts para evitar detecção
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
            
            logger.info("ChromeDriver configurado com sucesso")
            return self.driver
            
        except Exception as e:
            logger.error(f"Erro ao configurar ChromeDriver: {e}")
            raise
    
    def build_search_url(self, query: str, country: str = "BR", 
                        active_status: str = "active", 
                        ad_type: str = "all",
                        media_type: str = "all",
                        search_type: str = "keyword_exact_phrase") -> str:
        """Constrói a URL de busca baseada nos parâmetros"""
        params = {
            'active_status': active_status,
            'ad_type': ad_type,
            'country': country,
            'is_targeted_country': 'false',
            'media_type': media_type,
            'q': f'"{query}"',
            'search_type': search_type,
            'source': 'fb-logo'
        }
        
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Adiciona delay aleatório para simular comportamento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scroll_page(self, driver, scroll_pause_time=2):
        """Faz scroll na página para carregar mais conteúdo"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll para baixo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Aguarda carregar
            time.sleep(scroll_pause_time)
            
            # Calcula nova altura
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def extract_ad_data(self, ad_element) -> Dict:
        """Extrai dados de um anúncio específico"""
        try:
            ad_data = {
                'advertiser_name': '',
                'ad_text': '',
                'ad_type': '',
                'start_date': '',
                'end_date': '',
                'impressions': '',
                'spend': '',
                'demographics': {},
                'locations': [],
                'image_urls': [],
                'video_urls': [],
                'link_url': '',
                'ad_id': '',
                'platforms': [],
                'scraped_at': datetime.now().isoformat()
            }
            
            # Pega todo o texto do elemento
            element_text = ''
            try:
                element_text = ad_element.text.strip()
            except:
                pass
            
            # Extrai ID da biblioteca de anúncios
            try:
                if 'Identificação da biblioteca:' in element_text:
                    lines = element_text.split('\n')
                    for line in lines:
                        if 'Identificação da biblioteca:' in line:
                            ad_data['ad_id'] = line.replace('Identificação da biblioteca:', '').strip()
                            break
            except:
                pass
            
            # Extrai nome do anunciante - estratégias múltiplas
            advertiser_name = ''
            
            # Estratégia 1: Procura por texto antes de "Patrocinado"
            try:
                lines = element_text.split('\n')
                for i, line in enumerate(lines):
                    if 'Patrocinado' in line and i > 0:
                        potential_name = lines[i-1].strip()
                        if potential_name and len(potential_name) > 2 and len(potential_name) < 100:
                            advertiser_name = potential_name
                            break
            except:
                pass
            
            # Estratégia 2: Procura por links do Facebook
            if not advertiser_name:
                try:
                    links = ad_element.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href') or ''
                        text = link.text.strip()
                        if 'facebook.com' in href and text and len(text) > 2:
                            advertiser_name = text
                            break
                except:
                    pass
            
            # Estratégia 3: Procura na primeira linha válida
            if not advertiser_name:
                try:
                    lines = element_text.split('\n')
                    for line in lines[:10]:  # Verifica as primeiras 10 linhas
                        line = line.strip()
                        if (len(line) > 2 and len(line) < 100 and 
                            not any(word in line.lower() for word in [
                                'biblioteca', 'anúncios', 'filtros', 'resultado', 
                                'ativo', 'lançados', 'veiculação', 'plataformas'
                            ])):
                            advertiser_name = line
                            break
                except:
                    pass
            
            ad_data['advertiser_name'] = advertiser_name
            
            # Extrai texto do anúncio
            ad_text = ''
            try:
                # Procura por texto após "Patrocinado" até encontrar links ou metadata
                lines = element_text.split('\n')
                capturing = False
                captured_lines = []
                
                for line in lines:
                    line = line.strip()
                    
                    if 'Patrocinado' in line:
                        capturing = True
                        continue
                    
                    if capturing:
                        # Para de capturar se encontrar metadata ou links
                        if any(stop_word in line.lower() for stop_word in [
                            'ifood.com', 'facebook.com', 'identificação da biblioteca',
                            'veiculação iniciada', 'plataformas', 'ver detalhes'
                        ]):
                            break
                        
                        # Adiciona linha se for texto relevante
                        if line and len(line) > 5 and not line.startswith('#'):
                            captured_lines.append(line)
                            
                        # Limita a quantidade de texto
                        if len(captured_lines) >= 5:
                            break
                
                ad_text = ' '.join(captured_lines)
                
                # Se não conseguiu capturar assim, tenta outros métodos
                if not ad_text:
                    # Procura por parágrafos com texto significativo
                    text_elements = ad_element.find_elements(By.XPATH, ".//p | .//div[string-length(text()) > 30]")
                    texts = []
                    for elem in text_elements[:3]:
                        text = elem.text.strip()
                        if (len(text) > 30 and len(text) < 500 and 
                            'Identificação da biblioteca' not in text and
                            'Veiculação iniciada' not in text):
                            texts.append(text)
                    ad_text = ' '.join(texts)
                    
            except:
                pass
                
            ad_data['ad_text'] = ad_text[:500]  # Limita a 500 caracteres
            
            # Extrai data de início
            try:
                if 'Veiculação iniciada em' in element_text:
                    lines = element_text.split('\n')
                    for line in lines:
                        if 'Veiculação iniciada em' in line:
                            ad_data['start_date'] = line.strip()
                            break
            except:
                pass
            
            # Extrai URLs de imagens
            try:
                img_elements = ad_element.find_elements(By.TAG_NAME, "img")
                image_urls = []
                for img in img_elements:
                    src = img.get_attribute('src')
                    if src and ('scontent' in src or 'fbcdn' in src):
                        image_urls.append(src)
                ad_data['image_urls'] = image_urls[:3]  # Limita a 3 imagens
            except:
                pass
            
            # Extrai link de destino
            try:
                links = ad_element.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute('href') or ''
                    if any(domain in href for domain in ['ifood.com', 'instagram.com', 'whatsapp']):
                        ad_data['link_url'] = href
                        break
            except:
                pass
            
            # Só retorna se encontrou dados úteis
            if ad_data['advertiser_name'] or (ad_data['ad_text'] and len(ad_data['ad_text']) > 30):
                return ad_data
            else:
                return {}
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do anúncio: {str(e)}")
            return {}
    
    def search_ads_by_location_and_type(self, location: str, business_type: str, 
                                      max_results: int = 50) -> List[Dict]:
        """Busca anúncios por localização e tipo de negócio"""
        try:
            # Monta query de busca
            query = f"{business_type} {location}"
            
            # Configura driver
            if not self.driver:
                self.setup_driver()
            
            # Constrói URL
            search_url = self.build_search_url(query)
            logger.info(f"Buscando anúncios para: {query}")
            logger.info(f"URL: {search_url}")
            
            # Acessa a página
            self.driver.get(search_url)
            self.human_delay(3, 5)
            
            # Aguarda carregar
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                logger.warning("Timeout aguardando carregar página")
            
            # Scroll para carregar mais anúncios
            self.scroll_page(self.driver)
            
            # Extrai anúncios
            ads_data = []
            
            # Aguarda a página carregar completamente
            self.human_delay(5, 8)
            
            # Debug: salva screenshot para verificar o que está sendo carregado
            try:
                self.driver.save_screenshot("debug_page.png")
                logger.info("Screenshot salvo como debug_page.png")
            except:
                pass
            
            # Debug: verifica se chegou na página correta
            current_url = self.driver.current_url
            page_title = self.driver.title
            logger.info(f"URL atual: {current_url}")
            logger.info(f"Título da página: {page_title}")
            
            # Verifica se há conteúdo na página
            page_source = self.driver.page_source
            if "ads/library" not in current_url.lower():
                logger.warning("Não está na página da biblioteca de anúncios")
                return []
            
            # Seletores mais robustos e específicos para anúncios individuais
            ad_selectors = [
                # Seletores mais específicos para anúncios individuais
                "div[data-testid='ad-card']",
                "div[role='article']",
                "div[data-ad-preview='message']",
                "div[data-testid='political-ad']",
                # Seletores baseados na estrutura da biblioteca de anúncios
                "div[style*='border'] > div > div",
                "div[class*='result']",
                # Fallback para containers que contenham informações de anúncios
                "div:has(a[href*='facebook.com']):has(img)",
            ]
            
            ads_found = []
            used_selector = None
            
            for selector in ad_selectors:
                try:
                    if ":has(" in selector:
                        # Para seletores CSS avançados, usa JavaScript
                        elements = self.driver.execute_script("""
                            // Procura por elementos que parecem ser anúncios individuais
                            const candidates = [];
                            const allDivs = document.querySelectorAll('div');
                            
                            allDivs.forEach(div => {
                                const text = div.textContent || '';
                                const hasLink = div.querySelector('a[href*="facebook.com"]') || div.querySelector('a[href*="ifood.com"]');
                                const hasImage = div.querySelector('img');
                                const hasPatrocinado = text.includes('Patrocinado') || text.includes('Sponsored');
                                const hasAdInfo = text.includes('Identificação da biblioteca') || text.includes('Veiculação iniciada');
                                
                                // Verifica se é um container de anúncio válido
                                if (hasPatrocinado && (hasLink || hasImage || hasAdInfo)) {
                                    // Verifica se não é um container muito grande (evita duplicatas)
                                    if (text.length < 2000) {
                                        candidates.push(div);
                                    }
                                }
                            });
                            
                            // Remove duplicatas baseado no conteúdo
                            const unique = [];
                            const seen = new Set();
                            
                            candidates.forEach(candidate => {
                                const key = candidate.textContent.substring(0, 100);
                                if (!seen.has(key)) {
                                    seen.add(key);
                                    unique.push(candidate);
                                }
                            });
                            
                            return unique;
                        """)
                        if elements:
                            ads_found = elements
                            used_selector = selector
                            break
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            # Filtra elementos duplicados
                            unique_elements = []
                            seen_texts = set()
                            
                            for elem in elements:
                                try:
                                    text = elem.text[:100]  # Primeiros 100 caracteres como chave
                                    if text not in seen_texts and len(text) > 20:
                                        seen_texts.add(text)
                                        unique_elements.append(elem)
                                except:
                                    continue
                            
                            if unique_elements:
                                ads_found = unique_elements
                                used_selector = selector
                                logger.info(f"Encontrados {len(ads_found)} elementos únicos com seletor: {selector}")
                                break
                except Exception as e:
                    logger.debug(f"Erro com seletor {selector}: {e}")
                    continue
            
            # Se não encontrou com seletores específicos, tenta busca mais focada
            if not ads_found:
                logger.warning("Tentando busca mais focada por anúncios...")
                try:
                    # Busca específica por elementos que contenham "Patrocinado"
                    elements = self.driver.execute_script("""
                        const ads = [];
                        const allElements = document.querySelectorAll('*');
                        
                        allElements.forEach(elem => {
                            const text = elem.textContent || '';
                            if (text.includes('Patrocinado') || text.includes('Sponsored')) {
                                // Procura o container pai que contenha o anúncio completo
                                let container = elem;
                                for (let i = 0; i < 5; i++) {
                                    container = container.parentElement;
                                    if (!container) break;
                                    
                                    const containerText = container.textContent || '';
                                    if (containerText.includes('Identificação da biblioteca') || 
                                        containerText.includes('Veiculação iniciada') ||
                                        containerText.length > 200) {
                                        ads.push(container);
                                        break;
                                    }
                                }
                            }
                        });
                        
                        // Remove duplicatas
                        const unique = [];
                        const seen = new Set();
                        
                        ads.forEach(ad => {
                            const key = ad.textContent.substring(0, 100);
                            if (!seen.has(key)) {
                                seen.add(key);
                                unique.push(ad);
                            }
                        });
                        
                        return unique.slice(0, 10); // Máximo 10 anúncios únicos
                    """)
                    
                    if elements:
                        ads_found = elements
                        used_selector = "busca_por_patrocinado"
                        
                except Exception as e:
                    logger.error(f"Erro na busca focada: {e}")
            
            if not ads_found:
                logger.warning("Nenhum anúncio encontrado com nenhum seletor")
                return []
            
            logger.info(f"Usando seletor: {used_selector}, encontrados {len(ads_found)} elementos únicos")
            
            # Extrai dados de cada anúncio com filtragem de duplicatas
            ads_data = []
            seen_ads = set()  # Para evitar duplicatas
            
            for i, ad_element in enumerate(ads_found[:max_results]):
                try:
                    ad_data = self.extract_ad_data(ad_element)
                    
                    if ad_data and (ad_data.get('advertiser_name') or ad_data.get('ad_text')):
                        # Cria uma chave única para identificar duplicatas
                        ad_key = f"{ad_data.get('advertiser_name', '')[:50]}_{ad_data.get('ad_text', '')[:100]}"
                        ad_key = ad_key.lower().replace(' ', '').replace('\n', '')
                        
                        if ad_key not in seen_ads:
                            seen_ads.add(ad_key)
                            ads_data.append(ad_data)
                            
                            # Log melhorado
                            advertiser = ad_data.get('advertiser_name', 'N/A')
                            text_preview = ad_data.get('ad_text', '')[:50]
                            ad_id = ad_data.get('ad_id', 'N/A')
                            logger.info(f"Anúncio {len(ads_data)} extraído: {advertiser} | ID: {ad_id} | Texto: {text_preview}...")
                        else:
                            logger.debug(f"Anúncio {i+1} ignorado (duplicata)")
                    else:
                        logger.debug(f"Anúncio {i+1} sem dados válidos")
                    
                    # Delay entre extrações
                    self.human_delay(0.3, 1.0)
                    
                except Exception as e:
                    logger.error(f"Erro ao extrair anúncio {i+1}: {str(e)}")
                    continue
            
            # Se não encontrou nenhum anúncio válido, retorna info de debug
            if not ads_data:
                logger.warning("Nenhum anúncio válido encontrado")
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Verifica se há indicação de que não há anúncios
                    if any(phrase in page_text.lower() for phrase in [
                        'nenhum resultado', 'no results', '0 resultado', 'sem anúncios'
                    ]):
                        logger.info("Página indica que não há anúncios para os critérios especificados")
                        return []
                    
                    # Cria um anúncio de debug apenas se necessário
                    debug_ad = {
                        'advertiser_name': 'Debug - Análise da página',
                        'ad_text': 'Página carregada mas nenhum anúncio específico foi extraído',
                        'debug_info': f"URL: {self.driver.current_url}",
                        'page_sample': page_text[:300] + "...",
                        'scraped_at': datetime.now().isoformat()
                    }
                    return [debug_ad]
                    
                except Exception as e:
                    logger.error(f"Erro no método de debug: {e}")
                    return []
            
            logger.info(f"Total de anúncios únicos extraídos: {len(ads_data)}")
            return ads_data
            
        except Exception as e:
            logger.error(f"Erro na busca de anúncios: {str(e)}")
            return []
    
    def analyze_competition(self, location: str, business_type: str) -> Dict:
        """Analisa a concorrência em uma localização específica"""
        ads_data = self.search_ads_by_location_and_type(location, business_type)
        
        if not ads_data:
            return {
                'total_ads': 0,
                'active_advertisers': 0,
                'competition_level': 'baixa',
                'top_advertisers': [],
                'ad_types': {},
                'average_spend': 0,
                'analysis_date': datetime.now().isoformat()
            }
        
        # Análise dos dados
        advertisers = {}
        ad_types = {}
        
        for ad in ads_data:
            advertiser = ad.get('advertiser_name', 'Unknown')
            if advertiser in advertisers:
                advertisers[advertiser] += 1
            else:
                advertisers[advertiser] = 1
            
            ad_type = ad.get('ad_type', 'unknown')
            if ad_type in ad_types:
                ad_types[ad_type] += 1
            else:
                ad_types[ad_type] = 1
        
        # Determina nível de concorrência
        total_ads = len(ads_data)
        active_advertisers = len(advertisers)
        
        if total_ads >= 50:
            competition_level = 'alta'
        elif total_ads >= 20:
            competition_level = 'média'
        else:
            competition_level = 'baixa'
        
        # Top anunciantes
        top_advertisers = sorted(advertisers.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_ads': total_ads,
            'active_advertisers': active_advertisers,
            'competition_level': competition_level,
            'top_advertisers': top_advertisers,
            'ad_types': ad_types,
            'analysis_date': datetime.now().isoformat(),
            'location': location,
            'business_type': business_type
        }
    
    def get_advertiser_info(self, advertiser_name: str) -> Dict:
        """Obtém informações específicas de um anunciante"""
        try:
            query = advertiser_name
            ads_data = self.search_ads_by_location_and_type("", query, max_results=100)
            
            if not ads_data:
                return {
                    'advertiser_name': advertiser_name,
                    'total_ads': 0,
                    'has_active_ads': False,
                    'ad_types': [],
                    'locations': [],
                    'last_ad_date': None
                }
            
            # Processa dados do anunciante
            ad_types = set()
            locations = set()
            latest_date = None
            
            for ad in ads_data:
                if ad.get('advertiser_name', '').lower() == advertiser_name.lower():
                    ad_types.add(ad.get('ad_type', 'unknown'))
                    
                    # Processa localizações se disponível
                    for location in ad.get('locations', []):
                        locations.add(location)
                    
                    # Processa datas
                    start_date = ad.get('start_date', '')
                    if start_date and ('Started' in start_date):
                        # Extrai data do texto
                        pass
            
            return {
                'advertiser_name': advertiser_name,
                'total_ads': len(ads_data),
                'has_active_ads': len(ads_data) > 0,
                'ad_types': list(ad_types),
                'locations': list(locations),
                'last_ad_date': latest_date,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do anunciante {advertiser_name}: {str(e)}")
            return {
                'advertiser_name': advertiser_name,
                'total_ads': 0,
                'has_active_ads': False,
                'error': str(e)
            }
    
    def close(self):
        """Fecha o driver e limpa recursos"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def check_establishment_by_address(self, maps_address: str) -> Dict:
        """Verifica se um estabelecimento tem anúncios baseado no endereço do Google Maps"""
        try:
            # Extrai informações do endereço
            address_info = self.parse_maps_address(maps_address)
            
            if not address_info:
                return {
                    'establishment_found': False,
                    'has_ads': False,
                    'error': 'Não foi possível extrair informações do endereço fornecido',
                    'maps_address': maps_address
                }
            
            # Busca por anúncios usando diferentes estratégias
            search_strategies = []
            
            # Estratégia 1: Nome do estabelecimento + cidade
            if address_info.get('name') and address_info.get('city'):
                search_strategies.append({
                    'query': f"{address_info['name']} {address_info['city']}",
                    'type': 'name_city'
                })
            
            # Estratégia 2: Nome do estabelecimento + bairro
            if address_info.get('name') and address_info.get('neighborhood'):
                search_strategies.append({
                    'query': f"{address_info['name']} {address_info['neighborhood']}",
                    'type': 'name_neighborhood'
                })
            
            # Estratégia 3: Apenas nome do estabelecimento
            if address_info.get('name'):
                search_strategies.append({
                    'query': address_info['name'],
                    'type': 'name_only'
                })
            
            # Estratégia 4: Busca por categoria + localização
            if address_info.get('category') and address_info.get('city'):
                search_strategies.append({
                    'query': f"{address_info['category']} {address_info['city']}",
                    'type': 'category_city'
                })
            
            all_ads = []
            matching_ads = []
            
            # Executa as estratégias de busca
            for strategy in search_strategies:
                logger.info(f"Buscando com estratégia {strategy['type']}: {strategy['query']}")
                
                try:
                    ads = self.search_ads_by_keywords(strategy['query'], max_results=20)
                    all_ads.extend(ads)
                    
                    # Verifica se algum anúncio corresponde ao estabelecimento
                    for ad in ads:
                        if self.is_matching_establishment(ad, address_info):
                            matching_ads.append({
                                **ad,
                                'match_strategy': strategy['type'],
                                'match_confidence': self.calculate_match_confidence(ad, address_info)
                            })
                    
                    # Se encontrou correspondências, não precisa continuar
                    if matching_ads:
                        break
                        
                except Exception as e:
                    logger.error(f"Erro na estratégia {strategy['type']}: {e}")
                    continue
            
            # Ordena por confiança da correspondência
            matching_ads.sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
            
            return {
                'establishment_found': len(matching_ads) > 0,
                'has_ads': len(matching_ads) > 0,
                'total_matching_ads': len(matching_ads),
                'total_ads_searched': len(all_ads),
                'matching_ads': matching_ads[:5],  # Top 5 correspondências
                'establishment_info': address_info,
                'maps_address': maps_address,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar estabelecimento: {e}")
            return {
                'establishment_found': False,
                'has_ads': False,
                'error': str(e),
                'maps_address': maps_address,
                'analysis_date': datetime.now().isoformat()
            }
    
    def parse_maps_address(self, maps_address: str) -> Dict:
        """Extrai informações do endereço do Google Maps"""
        try:
            # Parse básico do endereço - pode ser melhorado com regex mais complexas
            address_info = {
                'name': '',
                'street': '',
                'neighborhood': '',
                'city': '',
                'state': '',
                'category': '',
                'original_address': maps_address
            }
            
            # Estratégias para extrair informações
            address_lower = maps_address.lower()
            
            # Extrai nome do estabelecimento (geralmente vem antes do primeiro hífen ou vírgula)
            if ' - ' in maps_address:
                potential_name = maps_address.split(' - ')[0].strip()
                if len(potential_name) > 2 and len(potential_name) < 100:
                    address_info['name'] = potential_name
            elif ',' in maps_address:
                potential_name = maps_address.split(',')[0].strip()
                if len(potential_name) > 2 and len(potential_name) < 100:
                    address_info['name'] = potential_name
            
            # Identifica cidades principais do Brasil
            brazilian_cities = [
                'rio de janeiro', 'são paulo', 'brasília', 'salvador', 'fortaleza',
                'belo horizonte', 'manaus', 'curitiba', 'recife', 'porto alegre',
                'goiânia', 'belém', 'guarulhos', 'campinas', 'nova iguaçu',
                'são bernardo do campo', 'niterói', 'florianópolis'
            ]
            
            for city in brazilian_cities:
                if city in address_lower:
                    address_info['city'] = city.title()
                    break
            
            # Identifica bairros comuns (pode ser expandido)
            common_neighborhoods = [
                'copacabana', 'ipanema', 'leblon', 'botafogo', 'tijuca',
                'barra da tijuca', 'centro', 'zona sul', 'zona norte',
                'vila olímpia', 'pinheiros', 'vila madalena', 'morumbi'
            ]
            
            for neighborhood in common_neighborhoods:
                if neighborhood in address_lower:
                    address_info['neighborhood'] = neighborhood.title()
                    break
            
            # Identifica categorias de estabelecimento
            categories = {
                'restaurante': ['restaurante', 'bar', 'lanchonete', 'pizzaria', 'hamburgueria'],
                'academia': ['academia', 'fitness', 'crossfit', 'pilates'],
                'salão': ['salão', 'barbershop', 'barbearia', 'cabeleireiro'],
                'loja': ['loja', 'store', 'boutique', 'magazine'],
                'hotel': ['hotel', 'pousada', 'hostel'],
                'clínica': ['clínica', 'consultório', 'médico', 'dentista']
            }
            
            for category, keywords in categories.items():
                if any(keyword in address_lower for keyword in keywords):
                    address_info['category'] = category
                    break
            
            return address_info
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse do endereço: {e}")
            return None
    
    def search_ads_by_keywords(self, keywords: str, max_results: int = 20) -> List[Dict]:
        """Busca anúncios por palavras-chave (método simplificado)"""
        try:
            # Configura driver se necessário
            if not self.driver:
                self.setup_driver()
            
            # Constrói URL de busca
            search_url = self.build_search_url(keywords)
            logger.info(f"Buscando anúncios para palavras-chave: {keywords}")
            
            # Acessa a página
            self.driver.get(search_url)
            self.human_delay(2, 4)
            
            # Aguarda carregar
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                logger.warning("Timeout aguardando carregar página")
            
            # Busca anúncios usando a mesma lógica do método principal
            elements = self.driver.execute_script("""
                const ads = [];
                const allElements = document.querySelectorAll('*');
                
                allElements.forEach(elem => {
                    const text = elem.textContent || '';
                    if (text.includes('Patrocinado') || text.includes('Sponsored')) {
                        let container = elem;
                        for (let i = 0; i < 5; i++) {
                            container = container.parentElement;
                            if (!container) break;
                            
                            const containerText = container.textContent || '';
                            if (containerText.includes('Identificação da biblioteca') || 
                                containerText.length > 200) {
                                ads.push(container);
                                break;
                            }
                        }
                    }
                });
                
                // Remove duplicatas
                const unique = [];
                const seen = new Set();
                
                ads.forEach(ad => {
                    const key = ad.textContent.substring(0, 100);
                    if (!seen.has(key)) {
                        seen.add(key);
                        unique.push(ad);
                    }
                });
                
                return unique.slice(0, arguments[0]);
            """, max_results)
            
            # Extrai dados dos anúncios encontrados
            ads_data = []
            for element in elements:
                try:
                    ad_data = self.extract_ad_data(element)
                    if ad_data and (ad_data.get('advertiser_name') or ad_data.get('ad_text')):
                        ads_data.append(ad_data)
                except:
                    continue
            
            return ads_data
            
        except Exception as e:
            logger.error(f"Erro na busca por palavras-chave: {e}")
            return []
    
    def is_matching_establishment(self, ad: Dict, establishment_info: Dict) -> bool:
        """Verifica se um anúncio corresponde ao estabelecimento procurado"""
        try:
            ad_text = (ad.get('ad_text', '') + ' ' + ad.get('advertiser_name', '')).lower()
            
            # Verifica correspondência por nome
            if establishment_info.get('name'):
                name_lower = establishment_info['name'].lower()
                # Verifica correspondência exata ou parcial
                if name_lower in ad_text or any(word in ad_text for word in name_lower.split() if len(word) > 3):
                    return True
            
            # Verifica correspondência por localização
            location_matches = 0
            if establishment_info.get('city'):
                if establishment_info['city'].lower() in ad_text:
                    location_matches += 1
            
            if establishment_info.get('neighborhood'):
                if establishment_info['neighborhood'].lower() in ad_text:
                    location_matches += 1
            
            # Se tem correspondência de localização e categoria
            if location_matches > 0 and establishment_info.get('category'):
                if establishment_info['category'].lower() in ad_text:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar correspondência: {e}")
            return False
    
    def calculate_match_confidence(self, ad: Dict, establishment_info: Dict) -> float:
        """Calcula a confiança da correspondência entre anúncio e estabelecimento"""
        try:
            confidence = 0.0
            ad_text = (ad.get('ad_text', '') + ' ' + ad.get('advertiser_name', '')).lower()
            
            # Correspondência de nome (peso alto)
            if establishment_info.get('name'):
                name_lower = establishment_info['name'].lower()
                if name_lower in ad_text:
                    confidence += 0.6
                elif any(word in ad_text for word in name_lower.split() if len(word) > 3):
                    confidence += 0.3
            
            # Correspondência de cidade (peso médio)
            if establishment_info.get('city'):
                if establishment_info['city'].lower() in ad_text:
                    confidence += 0.2
            
            # Correspondência de bairro (peso médio)
            if establishment_info.get('neighborhood'):
                if establishment_info['neighborhood'].lower() in ad_text:
                    confidence += 0.15
            
            # Correspondência de categoria (peso baixo)
            if establishment_info.get('category'):
                if establishment_info['category'].lower() in ad_text:
                    confidence += 0.05
            
            return min(confidence, 1.0)  # Máximo 1.0
            
        except Exception as e:
            logger.error(f"Erro ao calcular confiança: {e}")
            return 0.0

# API Flask para integração
app = Flask(__name__)
CORS(app)

# Instância global do scraper
scraper = FacebookAdsLibraryScraper(headless=True)

@app.route('/')
def index():
    """Página inicial com documentação da API"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Ads Scraper API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; text-align: center; }
        h2 { color: #333; border-bottom: 2px solid #1877f2; padding-bottom: 10px; }
        .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #1877f2; }
        .method { background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .method.post { background: #ffc107; color: #000; }
        .method.get { background: #17a2b8; }
        code { background: #e9ecef; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
        .status { text-align: center; padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; color: #155724; }
        .example { background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Facebook Ads Scraper API</h1>
        
        <div class="status">
            <strong>✅ API está funcionando!</strong><br>
            Servidor rodando em: http://127.0.0.1:5000
        </div>
        
        <h2>📋 Endpoints Disponíveis</h2>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /api/health</h3>
            <p>Verifica se o serviço está funcionando</p>
            <div class="example">
                <strong>Exemplo:</strong><br>
                <code>GET http://127.0.0.1:5000/api/health</code>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/analyze-competition</h3>
            <p>Analisa a concorrência para um nicho específico</p>
            <div class="example">
                <strong>Payload:</strong>
                <pre>{"niche": "fitness", "location": "Brazil"}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/check-advertiser</h3>
            <p>Verifica anúncios de um anunciante específico</p>
            <div class="example">
                <strong>Payload:</strong>
                <pre>{"advertiser_name": "Nike"}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/check-establishment</h3>
            <p>Verifica se um estabelecimento tem anúncios ativos (retorna detalhes completos)</p>
            <div class="example">
                <strong>Payload:</strong>
                <pre>{"maps_address": "Balada Mix - R. Barata Ribeiro, 111 - Copacabana, Rio de Janeiro - RJ"}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/has-ads</h3>
            <p>Verificação rápida se um estabelecimento tem anúncios (retorna apenas boolean)</p>
            <div class="example">
                <strong>Payload:</strong>
                <pre>{"maps_address": "Av. Paulista, 1578 - Bela Vista, São Paulo - SP"}</pre>
                <strong>Resposta:</strong>
                <pre>{"has_ads": true}</pre>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/search-ads</h3>
            <p>Busca anúncios baseados em critérios específicos</p>
            <div class="example">
                <strong>Payload:</strong>
                <pre>{"keywords": "academia", "location": "Brazil", "business_type": "fitness"}</pre>
            </div>
        </div>
        
        <h2>🛠️ Como Usar</h2>
        <p>Esta API permite fazer scraping da biblioteca de anúncios do Facebook. Use as rotas acima para acessar diferentes funcionalidades.</p>
        
        <h3>Exemplo com cURL:</h3>
        <pre>curl -X POST http://127.0.0.1:5000/api/health</pre>
        
        <h3>Exemplo com Python:</h3>
        <pre>import requests

response = requests.post('http://127.0.0.1:5000/api/health')
print(response.json())</pre>
        
        <h2>📊 Status</h2>
        <p>Desenvolvido para análise de concorrência e pesquisa de mercado através da biblioteca de anúncios do Facebook.</p>
    </div>
</body>
</html>
    '''

@app.route('/api/analyze-competition', methods=['POST'])
def analyze_competition():
    """Analisa a concorrência em uma localização"""
    try:
        data = request.get_json()
        location = data.get('location', '')
        business_type = data.get('business_type', '')
        
        if not location or not business_type:
            return jsonify({
                'error': 'Localização e tipo de negócio são obrigatórios'
            }), 400
        
        analysis = scraper.analyze_competition(location, business_type)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/check-advertiser', methods=['POST'])
def check_advertiser():
    """Verifica se um anunciante específico tem anúncios ativos"""
    try:
        data = request.get_json()
        advertiser_name = data.get('advertiser_name', '')
        
        if not advertiser_name:
            return jsonify({
                'error': 'Nome do anunciante é obrigatório'
            }), 400
        
        advertiser_info = scraper.get_advertiser_info(advertiser_name)
        return jsonify(advertiser_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/search-ads', methods=['POST'])
def search_ads():
    """Busca anúncios por localização e tipo"""
    try:
        data = request.get_json()
        location = data.get('location', '')
        business_type = data.get('business_type', '')
        max_results = data.get('max_results', 50)
        
        if not location or not business_type:
            return jsonify({
                'error': 'Localização e tipo de negócio são obrigatórios'
            }), 400
        
        ads = scraper.search_ads_by_location_and_type(location, business_type, max_results)
        
        return jsonify({
            'ads': ads,
            'total_found': len(ads),
            'location': location,
            'business_type': business_type
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/check-establishment', methods=['POST'])
def check_establishment():
    """Verifica se um estabelecimento tem anúncios ativos baseado no endereço do Google Maps"""
    try:
        data = request.get_json()
        maps_address = data.get('maps_address', '')
        
        if not maps_address:
            return jsonify({
                'error': 'Endereço do Google Maps é obrigatório'
            }), 400
        
        result = scraper.check_establishment_by_address(maps_address)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/has-ads', methods=['POST'])
def has_ads():
    """Verifica se um estabelecimento tem anúncios ativos - retorna apenas boolean"""
    try:
        data = request.get_json()
        maps_address = data.get('maps_address', '')
        
        if not maps_address:
            return jsonify({
                'has_ads': False,
                'error': 'Endereço do Google Maps é obrigatório'
            }), 400
        
        result = scraper.check_establishment_by_address(maps_address)
        
        return jsonify({
            'has_ads': result.get('has_ads', False)
        })
        
    except Exception as e:
        return jsonify({
            'has_ads': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Verifica se o serviço está funcionando"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        scraper.close()
