#!/usr/bin/env python3
"""
Script de teste para verificar o texto do e-mail da segunda-feira
"""

from datetime import datetime, timedelta
import pytz
from app.config import TIMEZONE

def test_monday_email_text():
    """Testa o texto do e-mail da segunda-feira"""
    print("=== TESTE DO TEXTO DO E-MAIL DA SEGUNDA-FEIRA ===")
    
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    print(f"Data atual: {today.strftime('%d/%m/%Y')} ({today.strftime('%A')})")
    
    # Simular que é segunda-feira
    if today.weekday() == 0:  # Segunda-feira
        print("✅ Hoje é segunda-feira - será enviado o e-mail combinado")
        
        # Calcular período da Lok Sabha para o e-mail
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        month_names = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        start_day = last_monday.day
        end_day = last_sunday.day
        month = month_names[last_monday.month]
        year = last_monday.year
        
        if start_day == end_day:
            loksabha_period = f"{start_day} de {month} de {year}"
        else:
            loksabha_period = f"{start_day} a {end_day} de {month} de {year}"
        
        # Assunto do e-mail
        email_subject = f"Boletim Diplomático + Relatório Lok Sabha - {today.strftime('%d/%m/%Y')}"
        
        # Corpo do e-mail
        email_body = f"""Prezados/as colegas,

Segue em anexo:

1. Boletim Diplomático de {today.strftime('%d/%m/%Y')} (resumo dos comunicados, discursos e briefings do MEA)
2. Relatório Semanal Lok Sabha de {loksabha_period} (resumo das questions & answers da Lok Sabha ao MEA)

Atenciosamente,
Taciano S. Zimmermann
Embaixada do Brasil em Nova Délhi"""
        
        print(f"\n📧 ASSUNTO:")
        print(f"   {email_subject}")
        
        print(f"\n📝 CORPO DO E-MAIL:")
        print(email_body)
        
        print(f"\n📊 RESUMO:")
        print(f"   - Boletim: {today.strftime('%d/%m/%Y')}")
        print(f"   - Lok Sabha: {loksabha_period}")
        
    else:
        print("ℹ️  Hoje não é segunda-feira - será enviado apenas o Boletim Diplomático")
        print("   Para testar o e-mail combinado, execute em uma segunda-feira")

if __name__ == "__main__":
    test_monday_email_text()
