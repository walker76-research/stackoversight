# For basic Site class
from stackoversight.scraping.site import Site
# For site tags and sorts
from enum import Enum
# For proxy exception
import requests
# Need that mutable tuple my dude
from recordclass.mutabletuple import mutabletuple


class StackOverflow(Site):
    site = 'stackoverflow'
    api_url = 'https://api.stackexchange.com'
    api_version = '2.2'

    timeout_sec = 86400
    min_pause = 1 / 30
    page_size = 100
    limit = 10000

    fields = {'sort': 'sort',
              'order': 'order',
              'tag': 'tagged',
              'page': 'page',
              'page_size': 'pagesize',
              'from_date': 'fromdate',
              'to_date': 'todate',
              'max': 'max',
              'min': 'min',
              'site': 'site',
              'key': 'key',
              'back_off': 'backoff'}

    class Methods(Enum):
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

    def __init__(self, client_keys: list):
        sessions = [self.init_key(key) for key in client_keys]
        self.req_table = set()

        super(StackOverflow, self).__init__(sessions, self.timeout_sec, self.limit)

    def get_min_pause(self):
        return self.min_pause

    def create_parent_link(self, category=Methods.question.value, **kwargs):
        url = f'{self.api_url}/{self.api_version}/{category}'

        kwargs['site'] = self.site

        url_fields = ''
        for key in kwargs:
            if key in self.fields:
                if url_fields:
                    url_fields += '&'

                url_fields += f'{self.fields[key]}={kwargs[key]}'

        return url + url_fields

    def get_child_links(self, parent_link: str, pause=False, pause_time=None):
        response = self.process_request(parent_link, pause, pause_time)
        key = response[1]
        request_count = response[2]
        response = response[0].json()

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

        if self.fields['back_off'] in response:
            self.back_off = response[self.fields['back_off']]

        return links, has_more

    # as a hook for future needs
    def handle_request(self, url: str, key: str):
        url = f'{url}&{self.fields["key"]}={key}'
        self.req_table.add(url)

        return requests.get(url)

    def init_key(self, key: str):
        response = requests.get(f'{self.api_url}/{self.api_version}/{self.Methods.info.value}{self.fields["site"]}'
                                f'={self.site}&{self.fields["key"]}={key}').json()

        if response['quota_max'] != self.limit:
            raise ValueError

        return mutabletuple(self.limit - response['quota_remaining'], key)

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
