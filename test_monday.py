#!/usr/bin/env python3
"""
Script para testar o comportamento do sistema em diferentes dias da semana
"""

from app.scheduler import get_target_dates
from datetime import datetime, date
from app.logger import logger

def test_weekday_behavior():
    logger.info("=== TESTE DE COMPORTAMENTO POR DIA DA SEMANA ===")
    
    # Testar diferentes dias da semana
    test_dates = [
        date(2025, 8, 4),   # Segunda-feira
        date(2025, 8, 5),   # Terça-feira  
        date(2025, 8, 6),   # Quarta-feira
        date(2025, 8, 7),   # Quinta-feira
        date(2025, 8, 8),   # Sexta-feira
        date(2025, 8, 9),   # Sábado
        date(2025, 8, 10),  # Domingo
        date(2025, 8, 11),  # Segunda-feira (próxima)
    ]
    
    weekday_names = {
        0: 'Segunda-feira',
        1: 'Terça-feira', 
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    for test_date in test_dates:
        weekday = test_date.weekday()
        weekday_name = weekday_names[weekday]
        
        target_dates = get_target_dates(test_date)
        
        print(f"\n📅 {weekday_name} ({test_date.strftime('%d/%m/%Y')}):")
        print(f"   Buscará documentos de: {[d.strftime('%d/%m/%Y') for d in target_dates]}")
        
        if weekday == 0:  # Segunda-feira
            print(f"   ✅ Segunda-feira: busca sexta, sábado e domingo")
        else:
            print(f"   📋 Outros dias: busca apenas o dia anterior")

if __name__ == "__main__":
    test_weekday_behavior() 