import requests
import urllib.request
import time
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, **kwargs):
        try:
            self.url = kwargs['url']
        except KeyError:
            pass

    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def set_url(self, url):
        self.url = url
