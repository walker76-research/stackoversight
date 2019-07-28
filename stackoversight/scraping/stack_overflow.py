import logging
import threading
from enum import Enum

from recordclass.mutabletuple import mutabletuple

import requests
from stackoversight.scraping.abstractsite import AbstractSite


class StackOverflow(AbstractSite):
    site = 'stackoverflow'
    api_url = 'https://api.stackexchange.com'
    api_version = '2.2'

    limit = 10000
    timeout_sec = 86400

    min_pause = 1 / 30
    page_size = 100

    req_table_lock = threading.Lock()
    req_table = set()

    back_off_lock = threading.Lock()
    back_off = 0

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
        java = 'java'

        java = 'java'

    def __init__(self, client_keys: list):
        super(StackOverflow, self).__init__([self.init_key(key) for key in client_keys], self.timeout_sec, self.limit)

    def get_child_links(self, parent_link: str, pause=False, pause_time=None):
        response = self.process_request(parent_link, pause, pause_time)

        # TODO: handle None response
        key = response[1]
        request_count = response[2]
        response = response[0].json()

        has_more = response['has_more']
        quota_max = response['quota_max']
        quota_remaining = response['quota_remaining']
        links = [item['link'] for item in response['items']]

        if quota_max - quota_remaining != request_count:
            logging.warning(f'Request count for key {key} is off by {abs(quota_max - quota_remaining - request_count)}')

        if not links:
            logging.critical('Failing to pull from the site, raising exception.')
            raise requests.exceptions.RequestException

        if self.fields['back_off'] in response:
            logging.info(f'{threading.current_thread().getName()} received a back_off after processing {parent_link}')

            new_back_off = response[self.fields['back_off']]

            with self.back_off_lock:
                if self.back_off and self.back_off < new_back_off:
                    self.back_off = new_back_off

        return links, has_more

    def handle_request(self, link: str, key: str):
        link = f'{link}&{self.fields["key"]}={key}'

        # TODO: have this function return None if it has already been scraped
        with self.req_table_lock:
            if link not in self.req_table:
                self.req_table.add(link)
            else:
                logging.warning(f'{threading.current_thread().getName()} received a link, {link} that has already been'
                                f' scraped!')

        return requests.get(link)

    @staticmethod
    def create_parent_link(method=Methods.question.value, **kwargs):
        url = f'{StackOverflow.api_url}/{StackOverflow.api_version}/{method}'

        kwargs['site'] = StackOverflow.site

        url_fields = ''
        for key in kwargs:
            if key in StackOverflow.fields:
                if url_fields:
                    url_fields += '&'

                url_fields += f'{StackOverflow.fields[key]}={kwargs[key]}'

        url += url_fields
        logging.info(f'Parent link {url} created.')
        return url

    @staticmethod
    def init_key(key: str):
        response = requests.get(f'{StackOverflow.api_url}/{StackOverflow.api_version}/'
                                f'{StackOverflow.Methods.info.value}{StackOverflow.fields["site"]}='
                                f'{StackOverflow.site}&{StackOverflow.fields["key"]}={key}').json()

        if response['quota_max'] != StackOverflow.limit:
            # TODO: later on handle by updating the limit instead
            logging.critical('Limit does not match that returned by the site, raising exception.')
            raise ValueError

        return mutabletuple(StackOverflow.limit - response['quota_remaining'] + 1, key)

    @staticmethod
    def get_text(response: requests.Response):
        try:
            return [element.get_text() for element in
                    AbstractSite.cook_soup(response).find_all(attrs={'class': 'post-text'})]
        except:
            logging.debug(f'In thread {threading.current_thread().getName()} no post-text found in response.')
            return []

    @staticmethod
    def get_code(response: requests.Response):
        try:
            return [element.get_text() for element in AbstractSite.cook_soup(response).find_all('code')]
        except:
            logging.debug(f'In thread {threading.current_thread().getName()} no code found in response.')
            return []

    @staticmethod
    def get_min_pause():
        return StackOverflow.min_pause

    @staticmethod
    def clear_back_off():
        with StackOverflow.back_off_lock:
            prev_back_off = StackOverflow.back_off

            if StackOverflow.back_off:
                StackOverflow.back_off = 0

        return prev_back_off
