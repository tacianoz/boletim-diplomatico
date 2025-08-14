#!/usr/bin/env python3
"""
Script de teste para verificar o novo agendamento
"""

from datetime import datetime, timedelta
import pytz
from app.config import TIMEZONE
from app.logger import logger

def test_schedule_logic():
    """Testa a lógica do novo agendamento"""
    print("=== TESTE DO NOVO AGENDAMENTO ===")
    
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    print(f"Data atual: {today.strftime('%d/%m/%Y')} ({today.strftime('%A')})")
    
    # Testar lógica para segunda-feira
    if today.weekday() == 0:  # Segunda-feira
        print("✅ Hoje é segunda-feira - executará Boletim + Lok Sabha às 6h")
        print("   - Boletim: sábado e domingo anteriores")
        print("   - Lok Sabha: semana anterior (segunda a domingo)")
        
        # Calcular datas do boletim (sábado e domingo)
        sat = today - timedelta(days=2)
        sun = today - timedelta(days=1)
        print(f"   - Boletim: {sat.strftime('%d/%m/%Y')} e {sun.strftime('%d/%m/%Y')}")
        
        # Calcular datas da Lok Sabha (semana anterior)
        last_monday = today - timedelta(days=7)
        last_sunday = last_monday + timedelta(days=6)
        print(f"   - Lok Sabha: {last_monday.strftime('%d/%m/%Y')} a {last_sunday.strftime('%d/%m/%Y')}")
        
    else:  # Terça a domingo
        print("✅ Hoje não é segunda-feira - executará apenas Boletim às 6h")
        print("   - Boletim: dia anterior")
        
        # Calcular data do boletim (dia anterior)
        yesterday = today - timedelta(days=1)
        print(f"   - Boletim: {yesterday.strftime('%d/%m/%Y')}")
    
    print("\n=== RESUMO DO AGENDAMENTO ===")
    print("📅 Segunda-feira às 6h: Boletim Diplomático + Lok Sabha")
    print("📅 Terça a Sábado às 6h: Apenas Boletim Diplomático")
    print("📅 Domingo: Não executa")
    
    print("\n=== PARA TESTAR ===")
    print("Execute: python combined_main.py")
    print("Isso iniciará o scheduler com a nova configuração.")

if __name__ == "__main__":
    test_schedule_logic()
