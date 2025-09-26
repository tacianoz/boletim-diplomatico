import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict
from app.logger import logger
import time
import random
import re

class EnvironmentScraper:
    def __init__(self):
        self.base_url = 'http://www.pib.gov.in/Allrel.aspx?lang=1&reg=3'
        self.environment_ministry_id = "30"
        
    def get_environment_documents_for_dates(self, target_dates: List[date]) -> List[Dict]:
        """Busca documentos do Ministry of Environment para as datas especificadas"""
        logger.info(f"Buscando documentos do Ministry of Environment para datas: {target_dates}")
        
        # Usar Selenium para buscar documentos
        return self.fetch_environment_with_selenium(target_dates)
    
    def fetch_environment_with_selenium(self, target_dates: List[date]) -> List[Dict]:
        """Função para buscar documentos do Environment com seleção de filtros usando Selenium"""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        import time

        logger.info(f"🎯 Usando Selenium para buscar documentos do Environment para datas: {target_dates}")
        
        try:
            # Configurar Chrome em modo headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Inicializar o driver
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Acessar a página
                logger.info(f"🌐 Acessando: {self.base_url}")
                driver.get(self.base_url)
                
                # Aguardar a página carregar
                time.sleep(3)
                
                all_docs = []
                
                # Para cada data alvo, fazer uma busca específica
                for target_date in target_dates:
                    logger.info(f"Buscando documentos para data específica: {target_date}")

                    def wait_postback():
                        WebDriverWait(driver, 20).until(
                            lambda drv: drv.execute_script("return document.readyState") == "complete"
                        )
                        time.sleep(1.5)

                    # 1) Selecionar Ministério e aguardar postback
                    ministry_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMinistry"))
                    )
                    Select(ministry_dropdown).select_by_visible_text(
                        "Ministry of Environment, Forest and Climate Change"
                    )
                    logger.info("📋 Ministério selecionado; aguardando postback...")
                    wait_postback()

                    # Re-obter elementos após postback
                    year_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlYear"))
                    )
                    month_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMonth"))
                    )
                    day_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlday"))
                    )

                    # 2) Selecionar Ano e aguardar
                    Select(year_dropdown).select_by_value(str(target_date.year))
                    logger.info(f"📅 Ano selecionado: {target_date.year}; aguardando postback...")
                    wait_postback()

                    # RE-SELECIONAR MINISTÉRIO após mudança de ano
                    ministry_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMinistry"))
                    )
                    Select(ministry_dropdown).select_by_visible_text(
                        "Ministry of Environment, Forest and Climate Change"
                    )
                    logger.info("📋 Ministério re-selecionado após ano...")
                    wait_postback()

                    # 3) Selecionar Mês e aguardar
                    month_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMonth"))
                    )
                    Select(month_dropdown).select_by_value(str(target_date.month))
                    logger.info(f"📅 Mês selecionado: {target_date.month}; aguardando postback...")
                    wait_postback()

                    # RE-SELECIONAR MINISTÉRIO após mudança de mês
                    ministry_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMinistry"))
                    )
                    Select(ministry_dropdown).select_by_visible_text(
                        "Ministry of Environment, Forest and Climate Change"
                    )
                    logger.info("📋 Ministério re-selecionado após mês...")
                    wait_postback()

                    # 4) Selecionar Dia e aguardar (lista final deve estar correta)
                    day_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlday"))
                    )
                    Select(day_dropdown).select_by_value(str(target_date.day))
                    logger.info(f"📅 Dia selecionado: {target_date.day}; aguardando postback...")
                    wait_postback()

                    # RE-SELECIONAR MINISTÉRIO após mudança de dia
                    ministry_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMinistry"))
                    )
                    Select(ministry_dropdown).select_by_visible_text(
                        "Ministry of Environment, Forest and Climate Change"
                    )
                    logger.info("📋 Ministério re-selecionado após dia...")
                    wait_postback()

                    # 5) Ler a lista de press releases diretamente
                    anchors = driver.find_elements(By.TAG_NAME, "a")
                    docs_for_day = []
                    for a in anchors:
                        href = a.get_attribute("href") or ""
                        text = (a.text or "").strip()
                        if href and "pressreleasepage" in href.lower() and text and len(text) > 10:
                            # Extrair conteúdo do documento
                            content = self.extract_document_content(href)
                            docs_for_day.append({
                                'tipo': 'Ministry of Environment, Forest and Climate Change',
                                'title': text,
                                'link': href,
                                'date': target_date,
                                'content': content
                            })

                    all_docs.extend(docs_for_day)
                    logger.info(f"📊 Coletados {len(docs_for_day)} documentos listados para {target_date}")
                
                logger.info(f"📊 Selenium encontrou {len(all_docs)} documentos do Environment")
                
                return all_docs
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Erro no Selenium: {e}")
            return []
    
    def extract_document_content(self, url: str) -> str:
        """Extrai o conteúdo de um documento PIB usando requests e BeautifulSoup"""
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tentar diferentes seletores para encontrar o conteúdo
            content_selectors = [
                'div.content',
                'div.col-md-9',
                'div.main-content',
                'div.article-content',
                'div.post-content',
                'article',
                'div[class*="content"]',
                'div.press-release-content',
                'div.details',
                '#main-content',
                '.content-area'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(separator='\n', strip=True)
                    if content_text and len(content_text) > 100:  # Conteúdo substantivo
                        break
            
            if not content_text:
                # Fallback: pegar todo o texto da página, excluindo cabeçalhos e rodapés
                for unwanted in soup(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                content_text = soup.get_text(separator='\n', strip=True)
            
            # Limpar o conteúdo
            if content_text:
                lines = [line.strip() for line in content_text.split('\n') if line.strip()]
                content_text = '\n'.join(lines)
                
                # Limitar o tamanho para não sobrecarregar a API
                if len(content_text) > 4000:
                    content_text = content_text[:4000] + "..."
                
                return content_text
            
            return f"Ministry of Environment Release - {url}"
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo de {url}: {e}")
            return f"Ministry of Environment Release - Content extraction failed: {url}"
    
    def parse_environment_documents(self, html: str, target_date: date) -> List[Dict]:
        """Desativado: a filtragem por ministério é feita via verificação na página de detalhe com Selenium"""
        return []
