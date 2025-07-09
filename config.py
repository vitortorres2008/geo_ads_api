import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ScraperConfig:
    # Configurações do navegador
    HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30
    SCROLL_PAUSE_TIME: int = 2
    
    # Configurações de rate limiting
    MIN_DELAY: float = 1.0
    MAX_DELAY: float = 3.0
    REQUEST_DELAY: float = 2.0
    
    # Configurações de proxy (opcional)
    USE_PROXY: bool = False
    PROXY_LIST: List[str] = []
    
    # Configurações de busca
    MAX_RESULTS_PER_SEARCH: int = 100
    MAX_CONCURRENT_SEARCHES: int = 3
    
    # Configurações de cache
    CACHE_DURATION_HOURS: int = 24
    CACHE_DIR: str = "cache"
    
    # Configurações de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "scraper.log"
    
    # Seletores CSS (podem precisar ser atualizados)
    AD_SELECTORS: List[str] = [
        "[data-testid='ad-card']",
        "[data-testid='political-ad']",
        ".x1lliihq",
        "[role='article']"
    ]
    
    # Padrões de busca
    SEARCH_PATTERNS: Dict[str, List[str]] = {
        'restaurante': [
            'restaurante {location}',
            'comida {location}',
            'delivery {location}',
            'gastronomia {location}'
        ],
        'loja': [
            'loja {location}',
            'varejo {location}',
            'shopping {location}',
            'compras {location}'
        ],
        'servico': [
            'serviço {location}',
            'atendimento {location}',
            'empresa {location}'
        ]
    }