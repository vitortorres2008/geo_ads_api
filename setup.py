import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    requirements = [
        'numpy>=1.24.3',
        'selenium==4.15.2',
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'flask==2.3.3',
        'flask-cors==4.0.0',
        'pandas>=2.1.1',
        'webdriver-manager==4.0.1'
    ]
    
    # Primeiro instalar numpy
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'numpy>=1.24.3'])
    
    # Depois instalar o resto
    for req in requirements[1:]:  # Pular numpy que já foi instalado
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])

def setup_chromedriver():
    """Configura o ChromeDriver automaticamente"""
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.quit()
        print("ChromeDriver configurado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao configurar ChromeDriver: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['cache', 'logs', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório criado: {directory}")

if __name__ == "__main__":
    print("Configurando ambiente para Facebook Ads Scraper...")
    
    print("1. Instalando dependências...")
    install_requirements()
    
    print("2. Configurando ChromeDriver...")
    setup_chromedriver()
    
    print("3. Criando diretórios...")
    create_directories()
    
    print("Configuração concluída!")