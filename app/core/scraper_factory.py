"""
Factory for creating scrapers
"""
from app.infrastructure.scrapers.mea_scraper import MEAScraper
from app.infrastructure.scrapers.pm_scraper import PMScraper


def get_mea_scraper() -> MEAScraper:
    """Create and return MEA scraper instance"""
    return MEAScraper()


def get_pm_scraper() -> PMScraper:
    """Create and return PM scraper instance"""
    return PMScraper()

