# For basic Site class
from stackoversight.scraping.site import Site
# For site tags and sorts
from enum import Enum
# Use regex to filter links
import re
# For proxy exception
import requests
# For soup processing
from bs4 import BeautifulSoup
# Need that mutable tuple my dude
from recordclass.mutabletuple import mutabletuple


class StackOverflow(Site):
    # Stack Overflow limits each client id to 10000 requests per day, the timeout parameter is in seconds
    limit = None
    timeout_sec = 86400
    min_pause = 1 / 30
    api_version = '2.2'
    page_size = 100
    api_url = 'https://api.stackexchange.com'
    site = 'stackoverflow'

    def __init__(self, client_keys: list):
        sessions = [self.init_key(key) for key in client_keys]

        super(StackOverflow, self).__init__(sessions, self.timeout_sec, self.limit)

    prefixes = {'sort': 'sort',
                'order': 'order',
                'tag': 'tagged',
                'page': 'page',
                'page_size': 'pagesize',
                'from_date': 'fromdate',
                'to_date': 'todate',
                'max': 'max',
                'min': 'min',
                'site': 'site',
                'key': 'key'}

    class Categories(Enum):
        question = 'questions?'
        user = 'users?'
        info = 'info?'

    class Sorts(Enum):
        activity = 'activity'
        votes = 'votes'
        creation = 'creation'
        hot = 'hot'
        week = 'week'
        month = 'month'

    class Orders(Enum):
        ascending = 'asc'
        descending = 'desc'

    class Tags(Enum):
        python = 'python'
        python2 = 'python-2.7'
        python3 = 'python-3.x'

    def get_min_pause(self):
        return self.min_pause

    def create_parent_link(self, category=Categories.question.value, **kwargs):
        url = f'{self.api_url}/{self.api_version}/{category}'

        kwargs['site'] = self.site

        url_fields = ''
        for key in kwargs:
            if key in self.prefixes:
                if url_fields:
                    url_fields += '&'

                url_fields += f'{self.prefixes[key]}={kwargs[key]}'

        return url + url_fields

    def get_child_links(self, parent_link: str, pause=False, pause_time=None):
        soup = self.get_soup(parent_link, pause, pause_time)

        # TODO: this is all now broken :( will need to fix to adapt to the response from stackexchange API

        # search the parse tree for all with the <a> tag, which is for a hyperlink and use the href tag to get the
        # url from them
        links = [link.get('href') for link in soup.find_all('a')]

        # handle possible error
        if not links:
            print("The proxy is up but it is failing to pull from the site.")
            raise requests.exceptions.ProxyError

        # filter to make sure only processing non empty links with question followed by a number and drop duplicates
        links = list(set(filter(re.compile('/questions/[0-9]').search, [link for link in links if link])))

        # insert preceding url section if needed
        precede = parent_link.split('/questions/')[0]
        links = [precede + link if link.startswith('/') else link for link in links]

        # filter out those that are not on the same site as the parent url
        return [link for link in links if link.startswith(precede)]

    def handle_request(self, url: str, key: str):
        return requests.get(f'{url}&{self.prefixes["key"]}={key}')

    @staticmethod
    def get_text(soup: BeautifulSoup):
        try:
            return [element.get_text() for element in soup.find_all(attrs={'class': 'post-text'})]
        except:
            # can fail when none are found
            return []

    @staticmethod
    def get_code(soup: BeautifulSoup):
        try:
            return [element.get_text() for element in soup.find_all('code')]
        except:
            # can fail when none are found
            return []

    @staticmethod
    def get_category(url: str):
        return url.split('https://')[1].split('.')[0]

    @staticmethod
    def get_id(self, url: str):
        return url.split('/')[4]

    def init_key(self, key: str):
        response = requests.get(f'{self.api_url}/{self.api_version}/{self.Categories.info.value}{self.prefixes["site"]}'
                                f'={self.site}&{self.prefixes["key"]}={key}')
        response = response.json()

        # TODO: pull and use more info from this response
        if not self.limit:
            self.limit = response['quota_max']

        return mutabletuple(self.limit - response['quota_remaining'], key)
