# Credit to Ben Shaver for his guide on scraping stackoverflow

# To send out HTTP requests
import requests
# To parse the HTML documents
from bs4 import BeautifulSoup
# For nap time if were nice to the process and the site
from time import sleep
# For site request limit management
from stackoversight.scraper.site_balancer import SiteBalancer


class Site(object):
    def __init__(self, client_ids: list, limit: int, timeout_sec: int):
        self.balancer = SiteBalancer(client_ids, timeout_sec, limit)
        self.limit = limit
        self.timeout_sec = timeout_sec

    def pause(self, pause_time):
        if not pause_time and self.timeout_sec:
            pause_time = self.limit / self.timeout_sec

        sleep(pause_time)

    def create_parent_link(self, *args):
        raise NotImplementedError

    def get_child_links(self, *args):
        raise NotImplementedError

    def get_soup(self, url: str, pause=False, pause_time=None):
        # TODO: Set this up to wait on a signal from a timer thread so that it isn't a busy wait
        # get the next id to use or wait until one is ready
        while not self.balancer.is_ready():
            sleep(1)
            print(":(")

        # handle delay if set to spread out requests
        if pause:
            self.pause(pause_time)

        # TODO: implement usage of the client ids when making this request
        client_id = next(self.balancer)

        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        try:
            response = requests.get(url, verify=False)
        except:
            print("Make sure Archituethis is running or comment out setting the proxy environment variables!\n")
            raise requests.exceptions.ProxyError

        # mark the request as being made
        self.balancer.capture()

        # TODO: could potentially split things from here on out to another thread so that one is purely requesting
        #  and another is handling parsing the html doc
        html_doc = response.text
        # return a navigable parse tree so that we can find our way around the html doc
        soup = BeautifulSoup(html_doc, 'html.parser')

        return soup
