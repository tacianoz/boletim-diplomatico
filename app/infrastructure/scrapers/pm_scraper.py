"""
Prime Minister Scraper for PM Office Releases
"""
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict
from app.logger import logger
from app.config import PM_RELEASES_URL, SELENIUM_WAIT_TIME
from app.infrastructure.scrapers.base_scraper import BaseScraper
from urllib.parse import urlencode
import pytz
import time
import re


class PMScraper(BaseScraper):
    """Scraper for Prime Minister Releases"""
    
    def __init__(self):
        super().__init__()
        from app.config import TIMEZONE
        self.timezone = TIMEZONE
    
    def should_use_month_selection(self) -> bool:
        """Verifica se deve usar seleção de mês (apenas no primeiro dia do mês)"""
        tz = pytz.timezone(self.timezone)
        today = datetime.now(tz).date()
        return today.day == 1
    
    def _parse_pm_documents(self, html: str, target_dates: List[date]) -> List[Dict]:
        """Parse Prime Minister documents from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        docs = []
        seen_links = set()  # Para evitar duplicatas
        
        # Verificar se a página tem conteúdo relevante
        if 'Access Denied' in html or 'access denied' in html.lower():
            logger.error("Página retornou 'Access Denied'")
            return []
        
        # Buscar todos os <li> na página (método simples que funciona)
        list_items = soup.find_all('li')
        
        logger.info(f"Encontrados {len(list_items)} itens <li> para processar")
        
        for item in list_items:
            # Procurar por link dentro do <li>
            link_elem = item.find('a')
            if not link_elem:
                continue
            
            # Extrair título e link primeiro
            title = link_elem.get_text(strip=True)
            link = link_elem.get('href')
            
            # Corrigir URL se necessário
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = 'https://www.pib.gov.in' + link
                else:
                    link = 'https://www.pib.gov.in/' + link

            # Garantir que a URL está em inglês (lang=1)
            if link and 'pib.gov.in' in link:
                if 'lang=' not in link:
                    link = link + ('&' if '?' in link else '?') + 'lang=1'
                else:
                    link = re.sub(r'lang=\d+', 'lang=1', link)
            
            if not title or not link:
                continue
                
            # Extrair data - método que funciona: procurar "Posted on:" no texto
            doc_date = None
            item_text = item.get_text(strip=True)
            
            # Método que funciona: procurar "Posted on:" no texto do item
            if 'Posted on:' in item_text:
                # Extrair a parte após "Posted on:"
                date_part = item_text.split('Posted on:')[1].strip()
                # Pegar apenas a data (pode ter mais texto depois)
                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', date_part)
                if date_match:
                    date_str = date_match.group(1)
                    doc_date = self.parse_date_string(date_str)
                    logger.debug(f"Data extraída: {date_str} -> {doc_date}")
            
            # Fallback: tentar outros métodos apenas se o primeiro não funcionar
            if not doc_date:
                # Tentar span com publishdatesmall (estrutura antiga)
                date_span = item.find('span', class_='publishdatesmall')
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    if 'Posted on:' in date_text:
                        date_part = date_text.split('Posted on:')[1].strip()
                        doc_date = self.parse_date_string(date_part)
                        logger.debug(f"Data encontrada em publishdatesmall: {date_part} -> {doc_date}")
            
            if not doc_date:
                # Tentar span com fa-calendar (estrutura nova)
                calendar_span = item.find('span', class_='fa fa-calendar')
                if calendar_span:
                    parent_p = calendar_span.find_parent('p')
                    if parent_p:
                        date_text = parent_p.get_text(strip=True)
                        date_text = date_text.replace('fa-calendar', '').strip()
                        doc_date = self.parse_date_string(date_text)
                        logger.debug(f"Data encontrada em fa-calendar: {date_text} -> {doc_date}")
            
            if title and link and doc_date:
                # Filtrar por datas alvo
                if doc_date in target_dates:
                    # Verificar se já existe um documento com o mesmo link (evitar duplicatas)
                    if link not in seen_links:
                        seen_links.add(link)
                        logger.info(f"✅ Documento encontrado: {title[:50]}... - {doc_date}")
                        docs.append({
                            'tipo': 'Prime Minister Releases',
                            'title': title,
                            'link': link,
                            'date': doc_date
                        })
                    else:
                        logger.debug(f"Documento duplicado ignorado: {title[:50]}... - {link}")
                else:
                    logger.debug(f"Documento fora do range: {title[:50]}... - {doc_date} (procurando: {target_dates})")
            elif title and link:
                logger.warning(f"⚠️ Documento sem data encontrado: {title[:50]}...")
        
        logger.info(f"Total de documentos PM encontrados para {target_dates}: {len(docs)}")
        return docs

    def _extract_content_with_driver(self, driver, url: str) -> str:
        """Extrai conteúdo de uma página PIB usando driver Selenium já aberto"""
        from selenium.webdriver.common.by import By

        try:
            # Garantir que URL está em inglês
            if 'lang=' not in url:
                url = url + ('&' if '?' in url else '?') + 'lang=1'
            else:
                url = re.sub(r'lang=\d+', 'lang=1', url)

            logger.debug(f"Extraindo conteúdo de: {url}")
            driver.get(url)
            time.sleep(3)

            content_text = ""

            # PIB usa iframes para o conteúdo do artigo - tentar acessar o iframe
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute("src") or ""
                    if "PressReleasePage" in src or "PRID" in src:
                        logger.debug(f"Encontrado iframe com src: {src}")
                        driver.switch_to.frame(iframe)
                        time.sleep(2)

                        # Extrair conteúdo do iframe
                        body = driver.find_element(By.TAG_NAME, "body")
                        content_text = body.text.strip()
                        logger.debug(f"Conteúdo do iframe: {len(content_text)} chars")

                        # Voltar ao contexto principal
                        driver.switch_to.default_content()
                        break
            except Exception as e:
                logger.debug(f"Erro ao acessar iframe: {e}")
                driver.switch_to.default_content()

            # Se não encontrou no iframe, tentar pegar do meta description
            if not content_text or len(content_text) < 200:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    og_desc = soup.find('meta', property='og:description')
                    if og_desc and og_desc.get('content'):
                        content_text = og_desc.get('content')
                        logger.debug(f"Usando og:description: {len(content_text)} chars")
                except:
                    pass

            # Fallback: pegar texto do body
            if not content_text or len(content_text) < 100:
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    content_text = body.text.strip()
                except:
                    pass

            if content_text and len(content_text) > 100:
                return content_text

            logger.warning(f"Conteúdo muito curto para: {url}")
            return ""

        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo de {url}: {e}")
            return ""

    def _fetch_with_selenium(self, target_dates: List[date]) -> List[Dict]:
        """Fetch PM documents using Selenium with month selection"""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import Select
        
        if not target_dates:
            return []
        
        # Pegar o mês da primeira data alvo (implementação simples que funcionava)
        target_month = target_dates[0].month
        
        logger.info(f"Usando Selenium para buscar documentos do mês {target_month}")
        
        driver = None
        try:
            # Configurar Chrome (igual à implementação que funcionava)
            chrome_options = self.get_selenium_options()
            
            # Configurar ChromeDriver - tentar usar o do sistema primeiro
            from selenium.webdriver.chrome.service import Service
            import os
            
            chromedriver_path = '/usr/bin/chromedriver'
            logger.info(f"Verificando ChromeDriver em: {chromedriver_path}")
            logger.info(f"ChromeDriver existe: {os.path.exists(chromedriver_path)}")
            
            driver = None
            if os.path.exists(chromedriver_path):
                logger.info(f"✅ Usando ChromeDriver do sistema: {chromedriver_path}")
                try:
                    service = Service(chromedriver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ ChromeDriver inicializado com sucesso!")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inicializar ChromeDriver do sistema: {e}")
                    driver = None
            
            if not driver:
                logger.info("Tentando usar webdriver-manager...")
                # Fallback: usar webdriver-manager
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    logger.info("Usando webdriver-manager para baixar ChromeDriver")
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ ChromeDriver inicializado via webdriver-manager!")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao usar webdriver-manager: {e}")
                    # Último fallback: tentar sem service (pode funcionar se estiver no PATH)
                    logger.info("Tentando usar ChromeDriver do PATH...")
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        logger.info("✅ ChromeDriver inicializado do PATH!")
                    except Exception as e:
                        logger.error(f"❌ Erro ao inicializar ChromeDriver: {e}")
                        raise Exception(f"Não foi possível inicializar ChromeDriver: {e}")
            
            # Configurar timeouts
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)

            # Remover propriedade webdriver para evitar detecção
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            # Acessar URL com parâmetros lang=1&reg=3 diretamente (usando URL encoding correto)
            base_url = 'https://www.pib.gov.in/PMContents/PMContents.aspx'
            params = {'menuid': '1', 'lang': '1', 'reg': '3'}
            url = f"{base_url}?{urlencode(params)}"
            logger.info(f"Acessando: {url}")

            logger.info("Carregando página...")
            driver.get(url)
            logger.info(f"Página carregada. Título: {driver.title}")

            # Verificar se Access Denied
            if 'Access Denied' in driver.title or 'Access Denied' in driver.page_source:
                logger.error("Bloqueado pelo site - Access Denied")
                return []

            # Aguardar a página carregar
            time.sleep(3)

            # Encontrar o dropdown de mês usando find_element direto (mais simples e estável)
            logger.info("Buscando dropdown de mês...")
            month_dropdown = driver.find_element(By.ID, "ContentPlaceHolder1_ddlMonth")

            # Selecionar o mês correto
            logger.info(f"Selecionando mês: {target_month}")
            select = Select(month_dropdown)
            select.select_by_value(str(target_month))

            logger.info(f"Mês {target_month} selecionado")

            # Aguardar a página atualizar após seleção do mês
            time.sleep(2)
            
            # Pegar o HTML da página
            html = driver.page_source
            
            logger.info(f"HTML obtido, tamanho: {len(html)} caracteres")
            
            # Verificar se a página carregou corretamente
            if 'Access Denied' in html or 'access denied' in html.lower():
                logger.error("Página retornou 'Access Denied'")
                return []
            
            # Verificar se há conteúdo relevante
            if 'Posted on:' not in html:
                logger.warning("HTML não contém 'Posted on:' - pode ter estrutura diferente")
            
            # Fazer parsing dos documentos
            docs = self._parse_pm_documents(html, target_dates)

            logger.info(f"Selenium encontrou {len(docs)} documentos para {target_dates}")

            # Extrair conteúdo de cada documento com o driver ainda aberto
            if docs:
                logger.info(f"Extraindo conteúdo de {len(docs)} documentos...")
                for i, doc in enumerate(docs):
                    logger.info(f"Extraindo conteúdo [{i+1}/{len(docs)}]: {doc['title'][:50]}...")
                    content = self._extract_content_with_driver(driver, doc['link'])
                    doc['content'] = content if content else "Content not available for this document."

            return docs
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro no Selenium: {error_msg}")
            import traceback
            logger.debug(f"Traceback completo: {traceback.format_exc()}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def get_pm_releases(self, target_dates: List[date]) -> List[Dict]:
        """Get Prime Minister Releases for target dates"""
        logger.info(f"Buscando Prime Minister Releases para datas: {target_dates}")
        
        # Sempre usar Selenium para PM scraper devido a problemas de redirects no site
        logger.info("Usando Selenium para PM scraper (site tem problemas de redirects)")
        try:
            # _fetch_with_selenium já extrai o conteúdo de cada documento
            docs = self._fetch_with_selenium(target_dates)
        except Exception as e:
            logger.error(f"Erro ao usar Selenium para PM scraper: {e}")
            # Fallback: tentar busca normal (sem conteúdo completo)
            logger.warning("Tentando busca normal como fallback...")
            html = self.fetch_page(PM_RELEASES_URL)
            if not html:
                logger.error("Falha também na busca normal")
                return []
            docs = self._parse_pm_documents(html, target_dates)
            # Fallback: buscar conteúdo com método antigo
            for doc in docs:
                doc['content'] = self.extract_content(doc['link'])
                if not doc['content']:
                    doc['content'] = "Content not available for this document."

        logger.info(f"Encontrados {len(docs)} Prime Minister Releases")
        return docs

