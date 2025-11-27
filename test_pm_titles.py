#!/usr/bin/env python3
"""Test script to check PM titles"""
from app.infrastructure.scrapers.pm_scraper import PMScraper
from app.core.date_utils import get_target_dates
from app.font_manager import contains_unicode_chars
import sys

scraper = PMScraper()
target_dates = get_target_dates()
docs = scraper.get_pm_releases(target_dates)

print(f"Encontrados {len(docs)} documentos PM\n")
print("=" * 80)

for i, doc in enumerate(docs[:5], 1):
    title = doc['title']
    print(f"\n{i}. Título original:")
    print(f"   {title}")
    print(f"   Tamanho: {len(title)} caracteres")
    print(f"   Tem Unicode: {contains_unicode_chars(title)}")
    
    # Verificar caracteres
    print(f"   Primeiros 100 caracteres (repr): {repr(title[:100])}")
    
    # Verificar se tem caracteres especiais
    non_ascii = [c for c in title if ord(c) > 127]
    if non_ascii:
        print(f"   Caracteres não-ASCII encontrados: {len(non_ascii)}")
        print(f"   Exemplos: {non_ascii[:10]}")

