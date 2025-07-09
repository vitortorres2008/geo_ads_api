import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict
import hashlib
import os

class DataExporter:
    """Classe para exportar dados em diferentes formatos"""
    
    @staticmethod
    def to_json(data: List[Dict], filename: str):
        """Exporta dados para JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def to_csv(data: List[Dict], filename: str):
        """Exporta dados para CSV"""
        if not data:
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
    
    @staticmethod
    def to_excel(data: List[Dict], filename: str):
        """Exporta dados para Excel"""
        if not data:
            return
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

class CacheManager:
    """Gerencia cache para evitar requisições desnecessárias"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get_cache_key(self, query: str, location: str) -> str:
        """Gera chave única para cache"""
        key_string = f"{query}_{location}_{datetime.now().strftime('%Y-%m-%d')}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_data(self, cache_key: str) -> Dict:
        """Recupera dados do cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def save_to_cache(self, cache_key: str, data: Dict):
        """Salva dados no cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")