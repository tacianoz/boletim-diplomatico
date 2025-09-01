import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict, Optional
from app.logger import logger
import time
import random
import re

class UNStatementsScraper:
    def __init__(self):
        self.base_url = "https://pminewyork.gov.in"
        self.headers = {
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
        
        # URLs específicas para 2025 (pode ser parametrizada no futuro)
        self.urls = {
            'General Assembly': "https://pminewyork.gov.in/pageyeargen?id=eyJpdiI6InlMdUkxYU1wcHhZa3UyS0p5OTdwbXc9PSIsInZhbHVlIjoiN1cyUDBKaW1nOXdBcHdkTFpCTWhwQT09IiwibWFjIjoiYWE3NjMwOTJmZTUzZTg3MTNhMWNmMmU3OWEwYmM2MzIyZDE2MTk2NmM0YjMyZGRjZGZlZTkwYzliZDVhYmIxNiJ9",
            'Security Council': "https://pminewyork.gov.in/pageyearsec?id=eyJpdiI6Ik9YSVBkZGtURVwvTFZhS1FYdEl1RWx3PT0iLCJ2YWx1ZSI6Ijg2bUtQQnkwOHE5Z1EzMU5HcFRWa3c9PSIsIm1hYyI6IjE4YTFiYjgxYTY5NDVlYTk1ODQzYjVjOTQ4OTk1MDQzYjBhMjNhNTFlYTlhNWY3NTA3MTIzMWI0ODY1NGM0MDUifQ=="
        }

    def fetch_page(self, url: str) -> Optional[str]:
        """Busca a página com delay aleatório para evitar bloqueio"""
        try:
            time.sleep(random.uniform(1, 3))
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return None

    def parse_date_string(self, date_str: str) -> Optional[date]:
        """Converte string de data para objeto date"""
        try:
            # Padrões de data encontrados no site
            patterns = [
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # 28 August 2025
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # August 28, 2025
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 28/08/2025
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_str.strip())
                if match:
                    if len(match.groups()) == 3:
                        if pattern == r'(\d{1,2})\s+(\w+)\s+(\d{4})':
                            day, month_name, year = match.groups()
                        elif pattern == r'(\w+)\s+(\d{1,2}),?\s+(\d{4})':
                            month_name, day, year = match.groups()
                        else:  # pattern == r'(\d{1,2})/(\d{1,2})/(\d{4})'
                            day, month, year = match.groups()
                            return date(int(year), int(month), int(day))
                        
                        # Converter nome do mês para número
                        month_map = {
                            'january': 1, 'jan': 1,
                            'february': 2, 'feb': 2,
                            'march': 3, 'mar': 3,
                            'april': 4, 'apr': 4,
                            'may': 5,
                            'june': 6, 'jun': 6,
                            'july': 7, 'jul': 7,
                            'august': 8, 'aug': 8,
                            'september': 9, 'sep': 9, 'sept': 9,
                            'october': 10, 'oct': 10,
                            'november': 11, 'nov': 11,
                            'december': 12, 'dec': 12
                        }
                        
                        month_num = month_map.get(month_name.lower())
                        if month_num:
                            return date(int(year), month_num, int(day))
            
            logger.warning(f"Não foi possível parsear a data: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao parsear data '{date_str}': {e}")
            return None

    def extract_statement_content(self, url: str) -> str:
        """Extrai o conteúdo completo de um statement individual"""
        try:
            html = self.fetch_page(url)
            if not html:
                return ""
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procurar por conteúdo em diferentes seletores
            content_selectors = [
                'div.content',
                'div.main-content',
                'div.article-content',
                'div.post-content',
                'article',
                'div[class*="content"]',
                'div#innerContent'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(separator='\n', strip=True)
                    if len(content_text) > 100:
                        return content_text
            
            # Fallback: pegar todo o texto do body
            body = soup.find('body')
            if body:
                return body.get_text(separator='\n', strip=True)
            
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo de {url}: {e}")
            return ""

    def parse_statements_from_html(self, html: str, target_dates: List[date], statement_type: str) -> List[Dict]:
        """Parseia statements da página HTML baseado na estrutura fornecida"""
        soup = BeautifulSoup(html, 'html.parser')
        statements = []
        
        # Procurar pela div principal que contém os statements
        inner_content = soup.find('div', id='innerContent')
        if not inner_content:
            logger.warning("Não encontrou div#innerContent")
            return statements
        
        # Procurar por todas as listas ul com classe commonListing
        statement_lists = inner_content.find_all('ul', class_='commonListing')
        
        for ul in statement_lists:
            # Procurar por todos os li dentro da lista
            list_items = ul.find_all('li')
            
            for item in list_items:
                try:
                    # Extrair link e título
                    link_elem = item.find('a')
                    if not link_elem:
                        continue
                    
                    # Para UNSC, o título está dentro de <b> dentro do <a>
                    if statement_type == 'Security Council':
                        title_elem = link_elem.find('b')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        else:
                            title = link_elem.get_text(strip=True)
                    else:
                        title = link_elem.get_text(strip=True)
                    
                    if not title:
                        continue
                    
                    # Extrair URL
                    href = link_elem.get('href')
                    if not href:
                        continue
                    
                    # Construir URL completa baseada no tipo
                    if statement_type == 'Security Council':
                        if href.startswith('IndiaatUNSC'):
                            full_url = f"https://pminewyork.gov.in/{href}"
                        elif href.startswith('/'):
                            full_url = f"https://pminewyork.gov.in{href}"
                        elif not href.startswith('http'):
                            full_url = f"https://pminewyork.gov.in/{href}"
                        else:
                            full_url = href
                    else:  # General Assembly
                        if href.startswith('IndiaatUNGA'):
                            full_url = f"https://pminewyork.gov.in/{href}"
                        elif href.startswith('/'):
                            full_url = f"https://pminewyork.gov.in{href}"
                        elif not href.startswith('http'):
                            full_url = f"https://pminewyork.gov.in/{href}"
                        else:
                            full_url = href
                    
                    # Extrair quem proferiu o statement
                    speaker = ""
                    speaker_p = item.find('p', class_='size11')
                    if speaker_p:
                        speaker_text = speaker_p.get_text(strip=True)
                        if speaker_text.startswith('Statement by'):
                            speaker = speaker_text
                    
                    # Extrair data
                    statement_date = None
                    date_p = item.find_all('p', class_='size11')
                    for p in date_p:
                        p_text = p.get_text(strip=True)
                        if not p_text.startswith('Statement by') and re.search(r'\d{4}', p_text):
                            statement_date = self.parse_date_string(p_text)
                            break
                    
                    # Se não encontrou data específica, tentar extrair do contexto
                    if not statement_date:
                        # Procurar por data no texto do item
                        item_text = item.get_text()
                        date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', item_text)
                        if date_match:
                            statement_date = self.parse_date_string(date_match.group(0))
                    
                    # Filtrar por datas alvo
                    if statement_date and statement_date in target_dates:
                        # Extrair conteúdo do statement
                        content = self.extract_statement_content(full_url)
                        
                        statement = {
                            'tipo': f'UN {statement_type}',
                            'title': title,
                            'link': full_url,
                            'date': statement_date,
                            'speaker': speaker,
                            'content': content
                        }
                        statements.append(statement)
                        logger.info(f"Encontrado {statement_type} statement: {title} - {statement_date}")
                
                except Exception as e:
                    logger.error(f"Erro ao processar item: {e}")
                    continue
        
        return statements

    def get_statements_for_dates(self, target_dates: List[date]) -> List[Dict]:
        """Busca statements da ONU (General Assembly e Security Council) para as datas especificadas"""
        logger.info(f"Buscando statements da ONU para datas: {target_dates}")
        
        all_statements = []
        
        # Buscar statements de ambos os tipos
        for statement_type, url in self.urls.items():
            logger.info(f"Buscando {statement_type} statements...")
            
            html = self.fetch_page(url)
            if not html:
                logger.error(f"Não foi possível acessar a página de {statement_type} statements")
                continue
            
            # Parsear statements
            statements = self.parse_statements_from_html(html, target_dates, statement_type)
            all_statements.extend(statements)
            
            logger.info(f"Encontrados {len(statements)} {statement_type} statements")
        
        logger.info(f"Total de statements encontrados: {len(all_statements)}")
        
        # Remover duplicatas baseado no título
        seen_titles = set()
        unique_statements = []
        
        for statement in all_statements:
            title = statement['title']
            if title not in seen_titles:
                seen_titles.add(title)
                unique_statements.append(statement)
            else:
                logger.info(f"Removendo statement duplicado: {title}")
        
        logger.info(f"Statements após remoção de duplicatas: {len(unique_statements)}")
        
        return unique_statements

    def get_statement_summary(self, statement: Dict) -> str:
        """Gera um resumo do statement baseado nos dados disponíveis"""
        summary = f"Statement: {statement['title']}\n"
        
        if statement['speaker']:
            summary += f"Speaker: {statement['speaker']}\n"
        
        summary += f"Date: {statement['date']}\n"
        summary += f"URL: {statement['link']}\n"
        
        if statement['content']:
            # Limitar conteúdo para não ficar muito longo
            content_preview = statement['content'][:500] + "..." if len(statement['content']) > 500 else statement['content']
            summary += f"\nContent Preview:\n{content_preview}"
        
        return summary
