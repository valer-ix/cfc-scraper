import pytest

from scraper import Scraper


@pytest.fixture()
def scraper():
    scraper = Scraper('https://www.google.com/')
    return scraper


def test_scraper_setup(scraper):
    assert scraper.url_target == 'https://www.google.com/'
    assert scraper.url_target_netloc == 'www.google.com'


def test_scrape_url(scraper):
    scraper.scrape_url(scraper.url_target)
    assert scraper.soup is not None
