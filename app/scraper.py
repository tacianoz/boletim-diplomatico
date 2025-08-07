import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from app.logger import logger
import time
import random
import re

BASE_URLS = {
    'Press Releases': 'https://www.mea.gov.in/press-releases.htm?51/Press_Releases',
    'Speeches & Statements': 'https://www.mea.gov.in/Speeches-Statements.htm?50/Speeches__amp;_Statements',
    'Media Briefings': 'https://www.mea.gov.in/media-briefings.htm?49/Media_Briefings',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

def fetch_page(url):
    try:
        # Adicionar delay aleatório para evitar bloqueio
        time.sleep(random.uniform(1, 3))
        
        session = requests.Session()
        session.headers.update(HEADERS)
        
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error(f"Erro ao acessar {url}: {e}")
        return None

def parse_documents(html: str, tipo: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    docs = []
    
    # Tentar diferentes seletores para encontrar a lista de documentos
    selectors = [
        'ul.press-releases li',
        'ul.list li',
        'div.content ul li',
        'div.main-content ul li',
        'li:has(a[href*="press"])',
        'li:has(a[href*="speech"])',
        'li:has(a[href*="media"])',
        'ul li'  # Fallback genérico
    ]
    
    lista = None
    for selector in selectors:
        lista = soup.select(selector)
        if lista and len(lista) > 0:
            logger.info(f"Encontrou lista usando seletor: {selector}")
            break
    
    if not lista:
        # Fallback: procurar por qualquer link que pareça ser um documento
        links = soup.find_all('a', href=True)
        docs = []
        for link in links:
            href = link['href']
            if any(keyword in href.lower() for keyword in ['press', 'speech', 'media', 'statement']):
                title = link.get_text(strip=True)
                if title and len(title) > 10:  # Filtrar títulos muito curtos
                    full_link = 'https://www.mea.gov.in/' + href.lstrip('/') if href.startswith('/') else href
                    docs.append({
                        'tipo': tipo,
                        'title': title,
                        'link': full_link,
                        'date': datetime.now().date()  # Fallback para data atual
                    })
        return docs
    
    for item in lista:
        a = item.find('a') if item.name != 'a' else item
        if not a:
            continue
            
        title = a.get_text(strip=True)
        link = a['href']
        
        # Corrigir URLs quebradas
        if link.startswith('/'):
            link = 'https://www.mea.gov.in/' + link.lstrip('/')
        elif not link.startswith('http'):
            # Se não tem http e não começa com /, adicionar o domínio
            if link.startswith('press-releases') or link.startswith('Speeches') or link.startswith('media'):
                link = 'https://www.mea.gov.in/' + link
            else:
                link = 'https://www.mea.gov.in/' + link
        
        # Tentar extrair data de diferentes formas
        date = None
        
        # 1. Procurar por data na estrutura específica do site: <p><span class="fa fa-calendar"></span> August 06, 2025</p>
        calendar_span = item.find('span', class_='fa fa-calendar')
        if calendar_span:
            # Pegar o texto do parágrafo pai que contém a data
            parent_p = calendar_span.find_parent('p')
            if parent_p:
                date_text = parent_p.get_text(strip=True)
                # Remover o texto do ícone e pegar apenas a data
                date_text = date_text.replace('fa-calendar', '').strip()
                logger.info(f"Encontrou data no ícone calendar: {date_text}")
                date = parse_date_string(date_text)
        
        # 2. Procurar por outros seletores de data
        if not date:
            date_selectors = [
                'span.date',
                'span.time', 
                'span.published',
                'span.timestamp',
                'div.date',
                'div.time',
                'p span:contains("calendar")',
            ]
            
            for selector in date_selectors:
                date_tag = item.select_one(selector)
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    logger.info(f"Encontrou data em {selector}: {date_str}")
                    date = parse_date_string(date_str)
                    if date:
                        break
        
        # 3. Procurar por data no texto do item (incluindo ícones)
        if not date:
            # Pegar todo o texto do item para procurar datas
            item_text = item.get_text()
            logger.info(f"Procurando data no texto: {item_text[:100]}...")
            
            date_patterns = [
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # August 06, 2025
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # 06 August 2025
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD ou YYYY-MM-DD
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, item_text, re.IGNORECASE)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY-MM-DD
                            date = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d").date()
                        elif match.group(1).isdigit() and len(match.group(1)) <= 2:  # DD/MM/YYYY
                            date = datetime.strptime(f"{match.group(3)}-{match.group(2)}-{match.group(1)}", "%Y-%m-%d").date()
                        else:  # Month DD, YYYY
                            month_str = match.group(1)
                            day = match.group(2)
                            year = match.group(3)
                            date = datetime.strptime(f"{month_str} {day}, {year}", "%B %d, %Y").date()
                        logger.info(f"Data extraída do texto: {date}")
                        break
                    except Exception as e:
                        logger.warning(f"Erro ao parsear data '{match.group(0)}': {e}")
                        continue
        
        # 4. Procurar data na URL
        if not date:
            url_date_patterns = [
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            ]
            for pattern in url_date_patterns:
                match = re.search(pattern, link)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY-MM-DD
                            date = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d").date()
                        else:  # DD/MM/YYYY
                            date = datetime.strptime(f"{match.group(3)}-{match.group(2)}-{match.group(1)}", "%Y-%m-%d").date()
                        logger.info(f"Data extraída da URL: {date}")
                        break
                    except:
                        continue
        
        # Se não encontrou data, usar data atual
        if not date:
            date = datetime.now().date()
            logger.warning(f"Não foi possível extrair data para: {title}")
        
        docs.append({
            'tipo': tipo,
            'title': title,
            'link': link,
            'date': date
        })
    
    return docs

def parse_date_string(date_str: str) -> datetime.date:
    """Tenta parsear uma string de data em diferentes formatos"""
    if not date_str:
        return None
    
    date_formats = [
        '%B %d, %Y',      # August 06, 2025
        '%B %d %Y',       # August 06 2025
        '%d, %B %Y',      # 06, August 2025
        '%d %B %Y',       # 06 August 2025
        '%d/%m/%Y',       # 07/08/2025
        '%Y-%m-%d',       # 2025-08-07
        '%d-%m-%Y',       # 07-08-2025
        '%m/%d/%Y',       # 08/07/2025
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            continue
    
    return None

def get_documents_for_dates(target_dates: List[datetime.date]) -> List[Dict]:
    all_docs = []
    
    # Seletores específicos para cada seção
    section_selectors = {
        'Press Releases': [
            'ul.press-releases li',
            'ul.commonListing li',
            'li:has(a[href*="press-releases"])',
            'li:has(a[href*="press"])'
        ],
        'Speeches & Statements': [
            'ul.commonListing li',
            'li:has(a[href*="Speeches-Statements"])',
            'li:has(a[href*="speech"])'
        ],
        'Media Briefings': [
            'ul.commonListing li',
            'li:has(a[href*="media-briefings"])',
            'li:has(a[href*="media"])'
        ]
    }
    
    for tipo, url in BASE_URLS.items():
        logger.info(f"Buscando documentos em: {tipo}")
        html = fetch_page(url)
        if not html:
            continue
        
        # Usar seletores específicos para cada seção
        docs = parse_documents_with_selectors(html, tipo, section_selectors.get(tipo, ['ul li']))
        logger.info(f"Encontrados {len(docs)} documentos em {tipo}")
        
        # Filtrar por datas alvo
        for doc in docs:
            if doc['date'] and doc['date'] in target_dates:
                all_docs.append(doc)
    
    return all_docs

def parse_documents_with_selectors(html: str, tipo: str, selectors: List[str]) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    docs = []
    
    lista = None
    for selector in selectors:
        lista = soup.select(selector)
        if lista and len(lista) > 0:
            logger.info(f"Encontrou lista usando seletor: {selector}")
            break
    
    if not lista:
        logger.warning(f"Não encontrou lista de documentos para {tipo}")
        return docs
    
    for item in lista:
        a = item.find('a') if item.name != 'a' else item
        if not a:
            continue
            
        title = a.get_text(strip=True)
        link = a['href']
        
        # Corrigir URLs quebradas
        if link.startswith('/'):
            link = 'https://www.mea.gov.in/' + link.lstrip('/')
        elif not link.startswith('http'):
            # Se não tem http e não começa com /, adicionar o domínio
            if link.startswith('press-releases') or link.startswith('Speeches') or link.startswith('media'):
                link = 'https://www.mea.gov.in/' + link
            else:
                link = 'https://www.mea.gov.in/' + link
        
        # Tentar extrair data de diferentes formas
        date = None
        
        # 1. Procurar por data na estrutura específica do site: <p><span class="fa fa-calendar"></span> August 06, 2025</p>
        calendar_span = item.find('span', class_='fa fa-calendar')
        if calendar_span:
            # Pegar o texto do parágrafo pai que contém a data
            parent_p = calendar_span.find_parent('p')
            if parent_p:
                date_text = parent_p.get_text(strip=True)
                # Remover o texto do ícone e pegar apenas a data
                date_text = date_text.replace('fa-calendar', '').strip()
                logger.info(f"Encontrou data no ícone calendar: {date_text}")
                date = parse_date_string(date_text)
        
        # 2. Procurar por outros seletores de data
        if not date:
            date_selectors = [
                'span.date',
                'span.time', 
                'span.published',
                'span.timestamp',
                'div.date',
                'div.time',
                'p span:contains("calendar")',
            ]
            
            for selector in date_selectors:
                date_tag = item.select_one(selector)
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    logger.info(f"Encontrou data em {selector}: {date_str}")
                    date = parse_date_string(date_str)
                    if date:
                        break
        
        # 3. Procurar por data no texto do item (incluindo ícones)
        if not date:
            # Pegar todo o texto do item para procurar datas
            item_text = item.get_text()
            logger.info(f"Procurando data no texto: {item_text[:100]}...")
            
            date_patterns = [
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # August 06, 2025
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # 06 August 2025
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD ou YYYY-MM-DD
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, item_text, re.IGNORECASE)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY-MM-DD
                            date = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d").date()
                        elif match.group(1).isdigit() and len(match.group(1)) <= 2:  # DD/MM/YYYY
                            date = datetime.strptime(f"{match.group(3)}-{match.group(2)}-{match.group(1)}", "%Y-%m-%d").date()
                        else:  # Month DD, YYYY
                            month_str = match.group(1)
                            day = match.group(2)
                            year = match.group(3)
                            date = datetime.strptime(f"{month_str} {day}, {year}", "%B %d, %Y").date()
                        logger.info(f"Data extraída do texto: {date}")
                        break
                    except Exception as e:
                        logger.warning(f"Erro ao parsear data '{match.group(0)}': {e}")
                        continue
        
        # 4. Procurar data na URL
        if not date:
            url_date_patterns = [
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            ]
            for pattern in url_date_patterns:
                match = re.search(pattern, link)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY-MM-DD
                            date = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d").date()
                        else:  # DD/MM/YYYY
                            date = datetime.strptime(f"{match.group(3)}-{match.group(2)}-{match.group(1)}", "%Y-%m-%d").date()
                        logger.info(f"Data extraída da URL: {date}")
                        break
                    except:
                        continue
        
        # Se não encontrou data, usar data atual
        if not date:
            date = datetime.now().date()
            logger.warning(f"Não foi possível extrair data para: {title}")
        
        docs.append({
            'tipo': tipo,
            'title': title,
            'link': link,
            'date': date
        })
    
    return docs

def fetch_full_content(doc_link: str) -> str:
    html = fetch_page(doc_link)
    if not html:
        return ''
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Tentar diferentes seletores para o conteúdo principal
    content_selectors = [
        'div.content',
        'div.col-md-9',
        'div.main-content',
        'div.article-content',
        'div.post-content',
        'article',
        'div[class*="content"]'
    ]
    
    main = None
    for selector in content_selectors:
        main = soup.select_one(selector)
        if main:
            break
    
    if not main:
        # Fallback: pegar o body inteiro
        main = soup.find('body')
    
    if not main:
        return ''
    
    return main.get_text(separator='\n', strip=True)
