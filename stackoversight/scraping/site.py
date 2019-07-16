# Credit to Ben Shaver for his guide on scraping stackoverflow

# For the proxy error
import requests
# To parse the HTML documents
from bs4 import BeautifulSoup
# For nap time if we're nice to the process and the site
from time import sleep
# For site request limit management
import datetime
# For balancing client requests to the site
from stackoversight.scraping.site_balancer import SiteBalancer


class Site(object):
    def __init__(self, sessions: list, timeout_sec: int, limit: int):
        self.balancer = SiteBalancer(sessions, timeout_sec, limit)
        self.limit = limit
        self.timeout_sec = timeout_sec
        self.last_pause_time = None

    def pause(self, pause_time):
        # if a specific pause_time isn't given then spread requests evenly over the timeout
        if not pause_time and self.limit:
            pause_time = self.timeout_sec / self.limit

        # only wait the diff between the time already elapsed and the pause_time if needed
        if self.last_pause_time:
            time_elapsed = datetime.datetime.now().second - self.last_pause_time

            if time_elapsed < pause_time:
                sleep(pause_time - time_elapsed)
                self.last_pause_time = datetime.datetime.now().second
        else:
            sleep(pause_time)
            self.last_pause_time = datetime.datetime.now().second

    def create_parent_link(self, *args):
        raise NotImplementedError

    def get_child_links(self, *args):
        raise NotImplementedError

    def handle_request(self, url, session):
        raise NotImplementedError

    def get_soup(self, url: str, pause=False, pause_time=None):
        # handle delay if set to spread out requests
        if pause:
            self.pause(pause_time)

        # TODO: Set this up to wait on a signal from a timer thread so that it isn't a busy wait
        # get the next id to use or wait until one is ready
        while not self.balancer.is_ready():
            sleep(1)
            print(":(")

        session = next(self.balancer)

        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        try:
            response = self.handle_request(url, session)
        except:
            print("Make sure Archituethis is running or comment out setting the proxy environment variables!\n"
                  "Could also be an issue with your token?")
            raise requests.exceptions.ProxyError

        # mark the request as being made
        self.balancer.capture()

        # TODO: could potentially split things from here on out to another thread so that one is purely requesting
        #  and another is handling parsing the html doc
        html_doc = response.text
        # return a navigable parse tree so that we can find our way around the html doc
        soup = BeautifulSoup(html_doc, 'html.parser')

        return soup
