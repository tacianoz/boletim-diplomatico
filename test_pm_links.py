#!/usr/bin/env python3
"""Test PM scraper links"""
from app.infrastructure.scrapers.pm_scraper import PMScraper
from datetime import date

scraper = PMScraper()
target_date = date(2025, 11, 28)
docs = scraper.get_pm_releases([target_date])

print(f'Encontrados {len(docs)} documentos PM para {target_date}')
print('=' * 80)

for i, doc in enumerate(docs[:5], 1):
    print(f'\n{i}. {doc["title"][:80]}')
    print(f'   Data: {doc["date"]}')
    print(f'   Link: {doc["link"]}')
    print(f'   Link começa com http: {doc["link"].startswith("http")}')
    print(f'   Link é relativo: {not doc["link"].startswith("http")}')

