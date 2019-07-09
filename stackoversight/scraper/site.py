# Credit to Ben Shaver for his guide on scraping stackoverflow

# To send out HTTP requests
import requests
# To parse the HTML documents
from bs4 import BeautifulSoup
# For nap time if were nice to the process and the site
from time import sleep
# For site request limit management
from stackoversight.scraper.site_balancer import SiteBalancer


# noinspection PyTypeChecker
class Site(object):
    def __init__(self, client_ids: list, limit: int, timeout_sec: int):
        self.balancer = SiteBalancer(client_ids, timeout_sec, limit)
        self.limit = limit
        self.timeout_sec = timeout_sec

    def create_parent_link(self, *args):
        raise NotImplementedError

    def get_child_links(self, *args):
        raise NotImplementedError

    def get_parse_tree(self, url: str, pause=False, pause_time=None):
        # TODO: Set this up to wait on a signal from a timer thread so that it isn't a busy wait
        # get the next id to use or wait until one is ready
        while not self.balancer.is_ready():
            sleep(1)
            print(":(")

        # handle delay if set to spread out requests
        if pause:
            if not pause_time and self.timeout_sec:
                pause_time = self.limit / self.timeout_sec

            sleep(pause_time)

        # TODO: implement usage of the client ids when making this request
        client_id = next(SiteBalancer)
        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        response = requests.get(url, verify=False)
        # mark the request as being made
        self.balancer.capture()

        # TODO: could potentially split things from here on out to another thread so that one is purely requesting
        #  and another is handling parsing the html doc
        html_doc = response.text
        # make a navigable parse tree so that we can find our way around the html doc
        parse_tree = BeautifulSoup(html_doc, 'html.parser')

        return parse_tree

    def get_by_(self, source, pause=False, pause_time=5):
        if isinstance(source, str):
            parse_tree = self.get_parse_tree(source, pause, pause_time)
        elif isinstance(source, BeautifulSoup):
            parse_tree = source
        else:
            raise TypeError

        return parse_tree

    def get_by_tag_class(self, source, tag_class: str, get_all=True, pause=False, pause_time=5):
        source = self.get_by_(source, pause, pause_time)

        # to get element need to use the tag's class to specify, and not the tag itself
        try:
            # handle whether to get all or just the first post, which will be the question
            if get_all:
                content = [element.get_text() for element in source.find_all(attrs={'class': tag_class})]
            else:
                content = [source.find(attrs={'class': tag_class}).get_text()]
        except:
            # sometimes there wont be any matching tags
            return None

        return content

    def get_by_tag(self, source, tag: str, get_all=True, pause=False, pause_time=5):
        source = self.get_by_(source, pause, pause_time)

        # to get code need to use the tag
        try:
            # handle whether to get all or just the first post, which will be the question
            if get_all:
                content = [element.get_text() for element in source.find_all(tag)]
            else:
                content = [source.find(tag).get_text()]
        except:
            # sometimes there wont be any matching tags
            return None

        return content
