import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from typing import List, Dict
from app.logger import logger
import time
import random
import re

LOKSABHA_URL = 'https://www.mea.gov.in/lok-sabha.htm?61/Lok_Sabha'

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
    """Busca uma página web com delay aleatório para evitar bloqueio"""
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

def parse_date_string(date_str: str) -> datetime.date:
    """Tenta parsear uma string de data em diferentes formatos"""
    if not date_str:
        return None
    
    date_formats = [
        '%d %b %Y',       # 06 Aug 2025
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

def get_loksabha_questions_for_week(start_date: date, end_date: date) -> List[Dict]:
    """
    Busca questions & answers da Lok Sabha para um período específico
    start_date: segunda-feira da semana
    end_date: domingo da semana
    """
    logger.info(f"Buscando questions & answers da Lok Sabha de {start_date} a {end_date}")
    
    html = fetch_page(LOKSABHA_URL)
    if not html:
        logger.error("Não foi possível acessar a página da Lok Sabha")
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    questions = []
    
    # Procurar pela lista de questions & answers
    # Baseado na estrutura HTML fornecida, procurar por <ul class="commonListing newThemeSchemes">
    list_items = soup.find_all('li')
    
    for item in list_items:
        # Procurar por link dentro do <li>
        link_elem = item.find('a')
        if not link_elem:
            continue
        
        # Procurar por span com data (formato: <p><span class="fa fa-calendar"></span> August 08, 2025</p>)
        calendar_span = item.find('span', class_='fa fa-calendar')
        if not calendar_span:
            continue
        
        # Pegar o texto do parágrafo pai que contém a data
        parent_p = calendar_span.find_parent('p')
        if not parent_p:
            continue
        
        date_text = parent_p.get_text(strip=True)
        # Remover o texto do ícone e pegar apenas a data
        date_text = date_text.replace('fa-calendar', '').strip()
        
        # Parsear a data
        question_date = parse_date_string(date_text)
        if not question_date:
            continue
        
        # Verificar se a data está no período desejado
        if start_date <= question_date <= end_date:
            title = link_elem.get_text(strip=True)
            link = link_elem.get('href')
            
            # Corrigir URL se necessário
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = 'https://www.mea.gov.in' + link
                else:
                    link = 'https://www.mea.gov.in/' + link
            
            if title and link:
                questions.append({
                    'title': title,
                    'link': link,
                    'date': question_date
                })
                logger.info(f"Encontrada question: {title[:50]}... ({question_date})")
    
    logger.info(f"Total de questions encontradas para o período: {len(questions)}")
    return questions

def fetch_question_content(question_link: str) -> str:
    """Busca o conteúdo completo de uma question & answer específica"""
    html = fetch_page(question_link)
    if not html:
        return ''
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Procurar pelo conteúdo da question & answer
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

def get_weekly_loksabha_summary():
    """
    Função principal para buscar questions & answers da semana anterior
    (segunda-feira a domingo)
    """
    # Calcular datas da semana anterior
    today = datetime.now().date()
    days_since_monday = today.weekday()  # 0=segunda, 1=terça, ..., 6=domingo
    
    # Última segunda-feira
    last_monday = today - timedelta(days=days_since_monday + 7)
    # Último domingo
    last_sunday = last_monday + timedelta(days=6)
    
    logger.info(f"Buscando questions & answers da semana: {last_monday} a {last_sunday}")
    
    questions = get_loksabha_questions_for_week(last_monday, last_sunday)
    
    if not questions:
        logger.info("Nenhuma question & answer encontrada para a semana")
        return []
    
    # Buscar conteúdo completo de cada question
    for i, question in enumerate(questions):
        logger.info(f"Processando question {i+1}/{len(questions)}: {question['title'][:50]}...")
        question['content'] = fetch_question_content(question['link'])
        if not question['content']:
            question['content'] = "Content not available for this question."
    
    return questions
