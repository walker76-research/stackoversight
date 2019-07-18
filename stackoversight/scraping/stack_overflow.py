# For basic Site class
from stackoversight.scraping.site import Site
# For site tags and sorts
from enum import Enum
# For proxy exception
import requests
# Need that mutable tuple my dude
from recordclass.mutabletuple import mutabletuple


class StackOverflow(Site):
    # TODO: clean up fields, ie site and stack_overflow shouldn't both have a limit field...
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

    # TODO: this is all now broken :( will need to fix to adapt to the response from stackexchange API
    def get_child_links(self, parent_link: str, pause=False, pause_time=None):
        response = self.process_request(parent_link, pause, pause_time)
        key = response[1]
        request_count = response[2]
        response = response[0].json()

        # TODO: get info like back_off and such from the response here!!
        has_more = response['has_more']
        quota_max = response['quota_max']
        quota_remaining = response['quota_remaining']
        links = [item['link'] for item in response['items']]

        if quota_max - quota_remaining != request_count:
            print(f'Request count for key {key} is off by {abs(quota_max - quota_remaining - request_count)}')
            # raise ValueError

        if not links:
            print('The proxy is up but it is failing to pull from the site.')
            raise requests.exceptions.ProxyError

        # TODO: catch back_off field and set it

        return links

    # as a hook for future needs
    def handle_request(self, url: str, key: str):
        return requests.get(f'{url}&{self.prefixes["key"]}={key}')

    @staticmethod
    def get_text(response: requests.Response):
        try:
            return [element.get_text() for element in Site.cook_soup(response).find_all(attrs={'class': 'post-text'})]
        except:
            # can fail when none are found
            return []

    @staticmethod
    def get_code(response: requests.Response):
        try:
            return [element.get_text() for element in Site.cook_soup(response).find_all('code')]
        except:
            # can fail when none are found
            return []

    def init_key(self, key: str):
        response = requests.get(f'{self.api_url}/{self.api_version}/{self.Categories.info.value}{self.prefixes["site"]}'
                                f'={self.site}&{self.prefixes["key"]}={key}').json()

        return mutabletuple(self.limit - response['quota_remaining'], key)
