#!/usr/bin/env python3
"""
Teste local da lógica de datas
"""

from datetime import datetime, timedelta
import pytz

def test_date_logic():
    # Usar fuso horário da Índia
    tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(tz).date()
    weekday = today.weekday()  # 0=Segunda, 1=Terça, ..., 6=Domingo
    
    print(f"Data atual (Índia): {today}")
    print(f"Dia da semana: {weekday} (0=Segunda, 1=Terça, ..., 6=Domingo)")
    
    if weekday == 0:  # Segunda-feira
        # Buscar sábado e domingo
        saturday = today - timedelta(days=2)
        sunday = today - timedelta(days=1)
        target_dates = [saturday, sunday]
        print(f"Segunda-feira: buscando sábado ({saturday}) e domingo ({sunday})")
    else:
        # Outros dias: buscar apenas o dia anterior
        yesterday = today - timedelta(days=1)
        target_dates = [yesterday]
        print(f"{today.strftime('%A')}: buscando ontem ({yesterday})")
    
    print(f"Datas alvo: {target_dates}")
    return target_dates

if __name__ == "__main__":
    test_date_logic()
