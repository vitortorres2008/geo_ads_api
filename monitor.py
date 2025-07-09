import time
import requests
import json
from datetime import datetime
import logging
from typing import Dict, List
import sqlite3
import schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdMonitor:
    """Sistema de monitoramento contínuo de anúncios"""
    
    def __init__(self, db_path: str = "monitor.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Configura banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para histórico de monitoramento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ad_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                advertiser_name TEXT NOT NULL,
                location TEXT NOT NULL,
                business_type TEXT NOT NULL,
                has_ads BOOLEAN NOT NULL,
                total_ads INTEGER DEFAULT 0,
                competition_level TEXT DEFAULT 'unknown',
                monitored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(advertiser_name, location, business_type, date(monitored_at))
            )
        ''')
        
        # Tabela para alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                advertiser_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def monitor_advertiser(self, advertiser_name: str, location: str, business_type: str):
        """Monitora um anunciante específico"""
        try:
            # Fazer requisição para API
            response = requests.post("http://localhost:5000/api/check-advertiser", json={
                "advertiser_name": advertiser_name
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Salvar no banco
                self.save_monitoring_data(advertiser_name, location, business_type, data)
                
                # Verificar se precisa gerar alerta
                self.check_for_alerts(advertiser_name, data)
                
                logger.info(f"Monitoramento de {advertiser_name} concluído")
                return data
            else:
                logger.error(f"Erro ao monitorar {advertiser_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro no monitoramento de {advertiser_name}: {str(e)}")
            return None
    
    def save_monitoring_data(self, advertiser_name: str, location: str, 
                           business_type: str, data: Dict):
        """Salva dados de monitoramento no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ad_monitoring 
            (advertiser_name, location, business_type, has_ads, total_ads, monitored_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            advertiser_name,
            location,
            business_type,
            data.get('has_active_ads', False),
            data.get('total_ads', 0),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def check_for_alerts(self, advertiser_name: str, data: Dict):
        """Verifica se precisa gerar alertas"""
        # Verifica se começou a anunciar
        if data.get('has_active_ads', False):
            prev_data = self.get_previous_monitoring_data(advertiser_name)
            if prev_data and not prev_data.get('has_ads', False):
                self.create_alert(advertiser_name, 'new_advertiser', 
                                f'{advertiser_name} começou a anunciar!')
        
        # Verifica se parou de anunciar
        elif not data.get('has_active_ads', False):
            prev_data = self.get_previous_monitoring_data(advertiser_name)
            if prev_data and prev_data.get('has_ads', False):
                self.create_alert(advertiser_name, 'stopped_advertising',
                                f'{advertiser_name} parou de anunciar!')
    
    def get_previous_monitoring_data(self, advertiser_name: str) -> Dict:
        """Obtém dados anteriores de monitoramento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT has_ads, total_ads FROM ad_monitoring 
            WHERE advertiser_name = ? 
            ORDER BY monitored_at DESC 
            LIMIT 1 OFFSET 1
        ''', (advertiser_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'has_ads': bool(result[0]),
                'total_ads': result[1]
            }
        return None
    
    def create_alert(self, advertiser_name: str, alert_type: str, message: str):
        """Cria um alerta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (advertiser_name, alert_type, message)
            VALUES (?, ?, ?)
        ''', (advertiser_name, alert_type, message))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Alerta criado: {message}")
    
    def get_monitoring_report(self, days: int = 7) -> Dict:
        """Gera relatório de monitoramento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('''
            SELECT COUNT(*) as total_monitored,
                   SUM(CASE WHEN has_ads THEN 1 ELSE 0 END) as with_ads,
                   SUM(CASE WHEN has_ads THEN 0 ELSE 1 END) as without_ads
            FROM ad_monitoring 
            WHERE monitored_at >= datetime('now', '-{} days')
        '''.format(days))
        
        stats = cursor.fetchone()
        
        # Alertas recentes
        cursor.execute('''
            SELECT alert_type, COUNT(*) as count
            FROM alerts 
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY alert_type
        '''.format(days))
        
        alerts = cursor.fetchall()
        
        conn.close()
        
        return {
            'period_days': days,
            'total_monitored': stats[0] if stats else 0,
            'with_ads': stats[1] if stats else 0,
            'without_ads': stats[2] if stats else 0,
            'alerts_by_type': dict(alerts) if alerts else {},
            'generated_at': datetime.now().isoformat()
        }

# Configuração de tarefas agendadas
def setup_scheduled_monitoring():
    """Configura monitoramento agendado"""
    monitor = AdMonitor()
    
    # Lista de estabelecimentos para monitorar
    establishments_to_monitor = [
        {"name": "McDonald's", "location": "São Paulo", "type": "restaurante"},
        {"name": "Burger King", "location": "São Paulo", "type": "restaurante"},
        {"name": "KFC", "location": "São Paulo", "type": "restaurante"},
        # Adicione mais estabelecimentos aqui
    ]
    
    def run_monitoring():
        """Executa monitoramento de todos os estabelecimentos"""
        logger.info("Iniciando monitoramento agendado...")
        
        for establishment in establishments_to_monitor:
            monitor.monitor_advertiser(
                establishment["name"],
                establishment["location"],
                establishment["type"]
            )
            time.sleep(10)  # Delay entre monitoramentos
        
        logger.info("Monitoramento agendado concluído")
    
    # Agendar monitoramento
    schedule.every().day.at("09:00").do(run_monitoring)  # Diário às 9h
    schedule.every().day.at("18:00").do(run_monitoring)  # Diário às 18h
    
    # Executar agendador
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto

if __name__ == "__main__":
    # Para executar o monitoramento agendado
    setup_scheduled_monitoring()