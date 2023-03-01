import re
import json
import logging
from typing import List, Optional

import requests
import validators
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s - %(message)s')


class Scraper:
    def __init__(self, url_target: str) -> None:
        self.url_target: Optional[str] = None
        self.url_target_netloc: Optional[str] = None
        self.url_privacypolicy: Optional[str] = None
        self.set_url_target(url_target)

        self.soup: Optional[BeautifulSoup] = None
        self.external_resources: List = []

    def set_url_target(self, url_target: str) -> None:
        self.url_target = url_target
        self.url_target_netloc = urlparse(url_target).netloc

    def scrape_url(self, url: str) -> None:
        """Scrape the webpage"""
        response = requests.get(url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def write_external_resource_urls_to_json(self, url: str) -> None:
        """Write a list of all externally loaded resources to JSON"""
        self.scrape_url(url)
        self.external_resources = []
        for tag in self.soup.find_all(True):
            tag_url = None
            if tag.name == 'link' and tag.has_attr('href'):
                tag_url = tag['href']
            elif tag.name == 'script' and tag.has_attr('src'):
                tag_url = tag['src']
            elif tag.name == "meta" and tag.has_attr("content"):
                tag_url = tag["content"]
            elif tag.name == "img" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "iframe" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "source" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "video" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "audio" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "embed" and tag.has_attr("src"):
                tag_url = tag["src"]
            elif tag.name == "object" and tag.has_attr("data"):
                tag_url = tag["data"]
            # If a URL has been found
            if tag_url:
                # If the URL is valid, and not a relative path
                if validators.url(tag_url):
                    # If the host location is not the current site
                    if urlparse(tag_url).netloc != self.url_target_netloc:
                        self.external_resources.append(tag_url)
        # Write to JSON
        filepath = 'output/external_resources.json'
        json.dump(self.external_resources, open(filepath, 'w'), indent=2)
        logging.info(f'External resources written to <{filepath}>.')

    def get_privacypolicy_url(self) -> None:
        """Enumerate the page's hyperlinks and identify the location of the "Privacy Policy" page"""
        if not self.soup:
            logging.error('Missing soup; must scrape a URL first.')
            return
        for link in self.soup.find_all('a'):
            if link.has_attr('href'):
                if 'privacy' in link['href']:
                    self.url_privacypolicy = link['href']
                    logging.info('Privacy Policy URL found.')
                    break
        if self.url_privacypolicy:
            # Make absolute url from relative
            if self.url_privacypolicy.startswith('/'):
                self.url_privacypolicy = urljoin(self.url_target, self.url_privacypolicy)
        else:
            logging.warning('Privacy Policy not found.')

    def write_word_count_to_json(self, url: str) -> None:
        """Produce a case-insensitive word frequency count for all the visible text on the page"""
        if url:
            self.scrape_url(url)

            word_counts = {}
            soup_text = self.soup.get_text()
            # Use regex to remove non-word characters
            for word in re.split(r'\W+', soup_text):
                # If word is not an empty string
                if word:
                    word = word.lower()
                    word_counts[word] = word_counts.get(word, 0) + 1
            word_counts = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))
            filepath = 'output/word_counts_privacypolicy.json'
            json.dump(word_counts, open(filepath, 'w'), indent=2)
            logging.info(f'Word counts written to <{filepath}>.')
        else:
            logging.error('URL invalid.')


if __name__ == '__main__':
    scraper = Scraper('https://www.cfcunderwriting.com/')
    scraper.write_external_resource_urls_to_json(scraper.url_target)
    scraper.get_privacypolicy_url()
    scraper.write_word_count_to_json(scraper.url_privacypolicy)
