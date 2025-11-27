#!/usr/bin/env python3
"""Test script to check if PM release page has English title"""
from app.infrastructure.scrapers.base_scraper import BaseScraper

scraper = BaseScraper()
# Test URL from the HTML
url = "https://www.pib.gov.in/PressReleseDetail.aspx?PRID=2195110"

html = scraper.fetch_page(url)
if html:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for title in various places
    print("Procurando título em inglês na página:\n")
    
    # Check h1, h2, h3
    for tag in ['h1', 'h2', 'h3']:
        elems = soup.find_all(tag)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 10:
                print(f"{tag}: {text[:200]}")
    
    # Check title attribute
    title_tag = soup.find('title')
    if title_tag:
        print(f"\ntitle tag: {title_tag.get_text(strip=True)}")
    
    # Check meta tags
    meta_title = soup.find('meta', property='og:title')
    if meta_title:
        print(f"og:title: {meta_title.get('content', '')}")
    
    # Check for English text patterns
    print("\n\nProcurando por padrões em inglês:")
    body_text = soup.get_text()
    # Look for common English words
    english_patterns = ['Prime Minister', 'participates', 'Constitution Day', 'expresses', 'pride']
    for pattern in english_patterns:
        if pattern.lower() in body_text.lower():
            # Find context around the pattern
            idx = body_text.lower().find(pattern.lower())
            context = body_text[max(0, idx-50):idx+100]
            print(f"\nEncontrado '{pattern}' no contexto:")
            print(context[:200])

