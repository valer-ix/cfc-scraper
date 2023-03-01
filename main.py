import json
import requests
import validators
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# Scrape the index webpage
url_target = 'https://www.cfcunderwriting.com/'
url_target_netloc = urlparse(url_target).netloc
response = requests.get(url_target)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')


# Write a list of all externally loaded resources to JSON
external_resources = []
for tag in soup.find_all(True):
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
            if urlparse(tag_url).netloc != url_target_netloc:
                external_resources.append(tag_url)
# Write to JSON
json.dump(external_resources, open('external_resources.json', 'w'), indent=2)


# Enumerate the page's hyperlinks and identify the location of the "Privacy Policy" page
url_privacypolicy = None
for link in soup.find_all('a'):
    if link.has_attr('href'):
        if 'privacy' in link['href']:
            url_privacypolicy = link['href']

# Scrape the content of the privacy policy URL

# Produce a case-insensitive word frequency count for all the visible text on the page
