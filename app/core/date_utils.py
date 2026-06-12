"""
Date utilities for parsing and handling dates
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
import pytz
import re
from app.logger import logger


def parse_date_string(date_str: str) -> Optional[date]:
    """
    Tenta parsear uma string de data em diferentes formatos
    Suporta múltiplos formatos encontrados nos sites
    """
    if not date_str:
        return None
    
    date_formats = [
        '%d %b %Y',       # 06 Aug 2025
        '%B %d, %Y',      # August 06, 2025
        '%B %d %Y',       # August 06 2025
        '%d, %B %Y',      # 06, August 2025
        '%d %B %Y',       # 06 August 2025
        '%d %B, %Y',      # 06 August, 2025 (novo site do MEA)
        '%d %b, %Y',      # 06 Aug, 2025
        '%d/%m/%Y',       # 07/08/2025
        '%Y-%m-%d',       # 2025-08-07
        '%d-%m-%Y',       # 07-08-2025
        '%m/%d/%Y',       # 08/07/2025
    ]
    
    # Tentar formatos diretos primeiro
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            continue
    
    # Tentar regex patterns para formatos mais complexos
    date_patterns = [
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # August 06, 2025
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # 06 August 2025
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD ou YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            try:
                if len(match.group(1)) == 4:  # YYYY-MM-DD
                    return datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d").date()
                elif match.group(1).isdigit() and len(match.group(1)) <= 2:  # DD/MM/YYYY
                    return datetime.strptime(f"{match.group(3)}-{match.group(2)}-{match.group(1)}", "%Y-%m-%d").date()
                else:  # Month DD, YYYY
                    month_str = match.group(1)
                    day = match.group(2)
                    year = match.group(3)
                    return datetime.strptime(f"{month_str} {day}, {year}", "%B %d, %Y").date()
            except Exception as e:
                logger.warning(f"Erro ao parsear data '{match.group(0)}': {e}")
                continue
    
    logger.warning(f"Não foi possível parsear a data: {date_str}")
    return None


def get_target_dates(today: Optional[date] = None) -> List[date]:
    """
    Retorna as datas alvo baseado no dia da semana
    Segunda-feira: sábado e domingo anteriores
    Outros dias: dia anterior
    """
    from app.config import TIMEZONE
    
    tz = pytz.timezone(TIMEZONE)
    if today is None:
        today = datetime.now(tz).date()
    
    weekday = today.weekday()  # 0=segunda, 1=terça, ..., 6=domingo
    
    if weekday == 0:  # Segunda-feira
        # Buscar sábado e domingo anteriores
        saturday = today - timedelta(days=2)
        sunday = today - timedelta(days=1)
        return [saturday, sunday]
    else:
        # Outros dias: buscar apenas o dia anterior
        return [today - timedelta(days=1)]

