#!/usr/bin/env python3
"""Test script to check if PM URL with lang=1&reg=3 returns English titles"""
from app.infrastructure.scrapers.pm_scraper import PMScraper
from app.core.date_utils import get_target_dates
from app.font_manager import contains_unicode_chars

scraper = PMScraper()
target_dates = get_target_dates()
docs = scraper.get_pm_releases(target_dates)

print(f"Encontrados {len(docs)} documentos PM\n")
print("=" * 80)

for i, doc in enumerate(docs[:5], 1):
    title = doc['title']
    print(f"\n{i}. Título:")
    print(f"   {title}")
    print(f"   Tem Unicode (Hindi): {contains_unicode_chars(title)}")
    print(f"   É inglês: {not contains_unicode_chars(title)}")

