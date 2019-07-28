import logging
import threading
import time
from time import sleep

import requests
from bs4 import BeautifulSoup
from stackoversight.scraping.site_balancer import SiteBalancer


class AbstractSite(object):

    def __init__(self, sessions: list, timeout_sec: int, limit: int):
        self.limit = limit
        self.timeout_sec = timeout_sec

        self.pause_lock = threading.Lock()
        self.last_pause_time = None

        self.balancer = SiteBalancer(sessions, timeout_sec, limit)

    def pause(self, pause_time):
        if not pause_time and self.limit:
            # try to evenly spread the requests out by default
            pause_time = self.timeout_sec / self.limit

        # this is the minimum wait between requests to not be throttled
        min_pause = self.get_min_pause()
        if pause_time < min_pause:
            pause_time = min_pause

        # only wait the diff between the time already elapsed from the last request and the pause_time
        if self.last_pause_time:
            time_elapsed = time.time() - self.last_pause_time

            # if the elapsed time is longer then no need to wait
            if time_elapsed < pause_time:
                pause_time -= time_elapsed
            else:
                pause_time = 0

        with self.pause_lock:
            # can not wait less than the back off field if it is set
            # returns the field to zero as it should be set only each time it is returned by the api
            # TODO: eventually this back_off field could be tied to the method called, and only threads using that
            #  method must wait the extra
            back_off = self.clear_back_off()
            if pause_time < back_off:
                pause_time = back_off

                logging.info(f'back_off in {threading.current_thread().getName()} is being handled')

            # initialize the last_pause_time field and sleep
            sleep(pause_time)
            self.last_pause_time = time.time()

        return self.last_pause_time

    def process_request(self, url: str, pause=False, pause_time=None):
        # get the next id to use or wait until one is ready
        self.balancer.ready.wait()

        key = next(self.balancer)

        # handle delay if set to spread out requests
        if pause:
            self.pause(pause_time)

        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        try:
            response = self.handle_request(url, key)
        except:
            logging.critical(f'In {threading.current_thread().getName()} error while requesting {url}, '
                             f'raising exception.')
            raise requests.exceptions.ProxyError

        # mark the request as being made
        request_count = self.balancer.capture()

        return response, key, request_count

    def create_parent_link(self, *args):
        raise NotImplementedError

    def get_child_links(self, *args):
        raise NotImplementedError

    def handle_request(self, url, session):
        raise NotImplementedError

    def get_min_pause(self):
        raise NotImplementedError

    def clear_back_off(self):
        raise NotImplementedError

    @staticmethod
    def cook_soup(response: requests.Response):
        return BeautifulSoup(response.text, 'html.parser')
