# For basic Site class
from stackoversight.scraper.site import Site
# For site tags and sorts
from enum import Enum
# Use regex to filter links
import re


class StackOverflow(Site):
    def __init__(self, client_ids: list):
        # Stack Overflow limits each client id to 10000 requests per day, the timeout parameter is in seconds
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

    def create_parent_link(self, category: Enum, tags=None, tab=None, sort=None, filter=None):
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

    def get_child_links(self, parent_link: str):
        parse_tree = self.get_parse_tree(parent_link)

        # search the parse tree for all with the <a> tag, which is for a hyperlink and use the href tag to get the
        # url from them
        links = [link.get('href') for link in parse_tree.find_all('a')]

        # filter to make sure only processing non empty links with question followed by a number and drop duplicates
        links = list(set(filter(re.compile('/questions/[0-9]').search, [link for link in links if link])))

        # insert preceding url section if needed
        precede = parent_link.split('/questions/')[0]
        links = [precede + link if link.startswith('/') else link for link in links]

        # filter out those that are not on the same site as the parent url
        links = [link for link in links if link.startswith(precede)]

        return links

    def get_text(self, url: str, pause=False, sleep_max=5):
        return self.get_by_tag_class(url, 'post-text', pause=pause, pause_time=sleep_max)

    def get_code(self, url: str, pause=False, sleep_max=5):
        return self.get_by_tag(url, 'code', pause=pause, pause_time=sleep_max)

    def get_category(self, url: str):
        return url.split('https://')[1].split('.')[0]

    def get_id(self, url: str):
        return url.split('/')[4]
