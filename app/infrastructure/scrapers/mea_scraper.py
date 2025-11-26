"""
MEA Scraper for Press Releases, Media Briefings, and Speeches & Statements
"""
from bs4 import BeautifulSoup
from datetime import datetime, date
from typing import List, Dict
from app.logger import logger
from app.config import (
    MEA_PRESS_RELEASES_URL,
    MEA_MEDIA_BRIEFINGS_URL,
    MEA_SPEECHES_URL
)
from app.infrastructure.scrapers.base_scraper import BaseScraper
import re


class MEAScraper(BaseScraper):
    """Scraper for MEA sections: Press Releases, Media Briefings, Speeches & Statements"""
    
    def __init__(self):
        super().__init__()
        self.section_selectors = {
            'MEA - Press Releases': [
                'ul.press-releases li',
                'ul.commonListing li',
                'li:has(a[href*="press-releases"])',
                'li:has(a[href*="press"])'
            ],
            'MEA - Speeches & Statements': [
                'ul.commonListing li',
                'li:has(a[href*="Speeches-Statements"])',
                'li:has(a[href*="speech"])'
            ],
            'MEA - Media Briefings': [
                'ul.commonListing li',
                'li:has(a[href*="media-briefings"])',
                'li:has(a[href*="media"])'
            ]
        }
    
    def _parse_documents_with_selectors(self, html: str, tipo: str, selectors: List[str], target_dates: List[date]) -> List[Dict]:
        """Parse documents from HTML using multiple selectors with fallback"""
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
                if link.startswith('press-releases') or link.startswith('Speeches') or link.startswith('media'):
                    link = 'https://www.mea.gov.in/' + link
                else:
                    link = 'https://www.mea.gov.in/' + link
            
            # Extrair data
            date = self._extract_date_from_item(item, link, title)
            
            # Filtrar por datas alvo
            if date and date in target_dates:
                docs.append({
                    'tipo': tipo,
                    'title': title,
                    'link': link,
                    'date': date
                })
        
        return docs
    
    def _extract_date_from_item(self, item, link: str, title: str) -> date:
        """Extract date from item using multiple strategies"""
        date = None
        
        # 1. Procurar por data na estrutura específica do site: <p><span class="fa fa-calendar"></span> August 06, 2025</p>
        calendar_span = item.find('span', class_='fa fa-calendar')
        if calendar_span:
            parent_p = calendar_span.find_parent('p')
            if parent_p:
                date_text = parent_p.get_text(strip=True)
                date_text = date_text.replace('fa-calendar', '').strip()
                logger.info(f"Encontrou data no ícone calendar: {date_text}")
                date = self.parse_date_string(date_text)
        
        # 2. Procurar por outros seletores de data
        if not date:
            date_selectors = [
                'span.date',
                'span.time', 
                'span.published',
                'span.timestamp',
                'div.date',
                'div.time',
            ]
            
            for selector in date_selectors:
                date_tag = item.select_one(selector)
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    logger.info(f"Encontrou data em {selector}: {date_str}")
                    date = self.parse_date_string(date_str)
                    if date:
                        break
        
        # 3. Procurar por data no texto do item
        if not date:
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
        
        return date
    
    def get_press_releases(self, target_dates: List[date]) -> List[Dict]:
        """Get MEA Press Releases for target dates"""
        logger.info(f"Buscando MEA Press Releases para datas: {target_dates}")
        html = self.fetch_page(MEA_PRESS_RELEASES_URL)
        if not html:
            return []
        
        docs = self._parse_documents_with_selectors(
            html, 
            'MEA - Press Releases', 
            self.section_selectors['MEA - Press Releases'],
            target_dates
        )
        
        # Buscar conteúdo completo
        for doc in docs:
            doc['content'] = self.extract_content(doc['link'])
            if not doc['content']:
                doc['content'] = "Content not available for this document."
        
        logger.info(f"Encontrados {len(docs)} MEA Press Releases")
        return docs
    
    def get_media_briefings(self, target_dates: List[date]) -> List[Dict]:
        """Get MEA Media Briefings for target dates"""
        logger.info(f"Buscando MEA Media Briefings para datas: {target_dates}")
        html = self.fetch_page(MEA_MEDIA_BRIEFINGS_URL)
        if not html:
            return []
        
        docs = self._parse_documents_with_selectors(
            html, 
            'MEA - Media Briefings', 
            self.section_selectors['MEA - Media Briefings'],
            target_dates
        )
        
        # Buscar conteúdo completo
        for doc in docs:
            doc['content'] = self.extract_content(doc['link'])
            if not doc['content']:
                doc['content'] = "Content not available for this document."
        
        logger.info(f"Encontrados {len(docs)} MEA Media Briefings")
        return docs
    
    def get_speeches_statements(self, target_dates: List[date]) -> List[Dict]:
        """Get MEA Speeches & Statements for target dates"""
        logger.info(f"Buscando MEA Speeches & Statements para datas: {target_dates}")
        html = self.fetch_page(MEA_SPEECHES_URL)
        if not html:
            return []
        
        docs = self._parse_documents_with_selectors(
            html, 
            'MEA - Speeches & Statements', 
            self.section_selectors['MEA - Speeches & Statements'],
            target_dates
        )
        
        # Buscar conteúdo completo
        for doc in docs:
            doc['content'] = self.extract_content(doc['link'])
            if not doc['content']:
                doc['content'] = "Content not available for this document."
        
        logger.info(f"Encontrados {len(docs)} MEA Speeches & Statements")
        return docs

