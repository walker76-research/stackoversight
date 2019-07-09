# Credit to Ben Shaver for his guide on scraping stackoverflow

# To send out HTTP requests
import requests
# To parse the HTML documents
from bs4 import BeautifulSoup
# To set the http_proxy environment variable
import os
# Use regex to filter links
import re
# For timing to avoid rate limiting
from random import randint
from time import sleep
# For StackOverflow info
from stackoversight.scraping.site.Site import *
# For site tags and sorts
from enum import Enum
# For load balancing client ids
import heapq
# For site request limit management
from stackoversight.scraping.site.SiteBalancer import *


class Site(object):
    def __init__(self, client_ids: list, limit: int, timeout_sec: int):
        self.balancer = SiteBalancer(client_ids, timeout_sec)
        self.limit = limit

    def create_parent_link(self):
        raise NotImplementedError

    def get_parse_tree(self, url: str, pause=False, sleep_max=5):
        # handle if 10,000 rate limit reached
        # peeks at top of heap, at the first entry in the tuple which is the request count
        while self.balancer.peek_top_count() >= self.limit:
            sleep(1)

        # handle delay if set to spread out requests
        if pause:
            sleep(randint(1, sleep_max))

        # TODO: implement usage of the client ids when making this request
        client_id = self.balancer.peek_top_client_id()
        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        response = requests.get(url, verify=False)
        # insert into release queue
        self.balancer.mark_request()

        # access the html doc
        html_doc = response.text
        # make a navigable parse tree so that we can find our way around the html doc
        soup = BeautifulSoup(html_doc, 'html.parser')

        return soup

    def get_child_links(self, parent_link: str):
        parse_tree = self.get_parse_tree(parent_link)

        links = []

        # search the parse tree for all with the <a> tag, which is for a hyperlink
        for link in parse_tree.find_all('a'):
            # use the href tag to get the url from them
            links.append((link.get('href')))

        # filter to make sure only processing non empty links with question followed by a number and drop duplicates
        links = list(set(filter(re.compile('/questions/[0-9]').search, [link for link in links if link])))

        # TODO will need better way to split this in the future
        # insert preceding url section if needed
        precede = parent_link.split('/questions/')[0]
        links = [precede + link if link.startswith('/') else link for link in links]

        # filter out those that are not on the same site as the parent url
        links = [link for link in links if link.startswith(precede)]

        return links

    def get_by_tag_class(self, url: str, tag_class: str, get_all=True, pause=False, sleep_max=5):
        parse_tree = get_parse_tree(url, pause, sleep_max)

        # to get text need to use the tag's class to specify, and not the tag itself
        try:
            # handle whether to get all or just the first post, which will be the question
            if get_all:
                content = [element.get_text() for element in parse_tree.find_all(attrs={'class': tag_class})]
            else:
                content = {parse_tree.find(attrs={'class': tag_class}).get_text()}
        except:
            # sometimes there wont be any matching tags
            return None

        return content

    def get_by_tag(self, url: str, tag: str, get_all=True, pause=False, sleep_max=5):
        parse_tree = get_parse_tree(url, pause, sleep_max)

        # to get code need to use the tag
        try:
            # handle whether to get all or just the first post, which will be the question
            if get_all:
                content = [element.get_text() for element in parse_tree.find_all(tag)]
            else:
                content = {parse_tree.find(tag).get_text()}
        except:
            # sometimes there wont be any matching tags
            return None

        return content


class StackOverflow(Site):
    def __init__(self, client_ids: list):
        # Stack Overflow limits each client id to 10000 requests per day
        # The timeout parameter is in seconds
        super(StackOverflow, self).__init__(client_ids, 9999, 86400)

    class Sorts(Enum):
        frequency = 'MostFrequent'
        bounty = 'BountyEndingSoon'
        vote = 'MostVotes'
        recent = 'RecentActivity'
        newest = 'Newest'

    class Filters(Enum):
        unanswered = 'NoAnswers'
        unaccepted = 'NoAcceptedAnswer'
        bounty = 'Bounty'

    class Tabs(Enum):
        newest = 'Newest'
        active = 'Active'
        bounty = 'Bounties'
        unanswered = 'Unanswered'
        frequent = 'Frequent'
        vote = 'Votes'

    class Tags(Enum):
        python = 'python'
        python2 = 'python-2.7'
        python3 = 'python-3.x'

    class Categories(Enum):
        question = 'questions'

    def create_parent_link(self, category: Enum, tags=[], tab=None, sort=None, filter=None):
        url = 'https://stackoverflow.com/'

        if category:
            url += category.value

        if tags:
            url += '/tagged/'
        for tag in tags:
            url += tag.value + '%20'
        if url.endswith('%20'):
            url = url[:-3]

        if tab:
            url += '/?tab=' + tab.value
        elif sort:
            url += '/?sort=' + sort.value

        if filter:
            url += '&filters=' + filter.value

        if tab or sort or filter:
            url += '&edited=true'

        return url

    def get_category(self, url: str):
        return url.split('https://')[1].split('.')[0]

    def get_id(self, url: str):
        return url.split('/')[4]

    def get_text(url: str, pause=False, sleep_max=5):
        return get_by_tag_class(url, 'post-text', pause=pause, sleep_max=sleep_max)

    def get_code(url: str, pause=False, sleep_max=5):
        return get_by_tag(url, 'code', pause=pause, sleep_max=sleep_max)