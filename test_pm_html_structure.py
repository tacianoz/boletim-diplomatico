#!/usr/bin/env python3
"""Test script to check PM HTML structure for English titles"""
from app.infrastructure.scrapers.pm_scraper import PMScraper
from app.core.date_utils import get_target_dates
from bs4 import BeautifulSoup
import re

scraper = PMScraper()
target_dates = get_target_dates()

# Fetch HTML using Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from app.config import SELENIUM_WAIT_TIME
import time

chrome_options = scraper.get_selenium_options()
driver = webdriver.Chrome(options=chrome_options)

url = 'https://www.pib.gov.in/PMContents/PMContents.aspx?menuid=1'
driver.get(url)
time.sleep(SELENIUM_WAIT_TIME)

month_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddlMonth"))
)

select = Select(month_dropdown)
select.select_by_value(str(target_dates[0].month))
time.sleep(SELENIUM_WAIT_TIME)

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')
list_items = soup.find_all('li')

print("Analisando estrutura HTML dos primeiros 3 itens com data:\n")
count = 0
for item in list_items:
    link_elem = item.find('a')
    if not link_elem:
        continue
    
    item_text = item.get_text(strip=True)
    if 'Posted on:' in item_text:
        date_match = re.search(r'Posted on:\s*(\d{1,2}\s+\w+\s+\d{4})', item_text)
        if date_match:
            date_str = date_match.group(1)
            from app.core.date_utils import parse_date_string
            doc_date = parse_date_string(date_str)
            if doc_date in target_dates:
                count += 1
                print(f"\n{'='*80}")
                print(f"Item {count}:")
                print(f"HTML completo do <li>:")
                print(item.prettify()[:1000])
                print(f"\nTexto do link: {link_elem.get_text(strip=True)}")
                print(f"Atributos do link: {link_elem.attrs}")
                if count >= 3:
                    break

