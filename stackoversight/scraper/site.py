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
from stackoversight.scraper.site_balancer import SiteBalancer
# For authentication and to send requests
from requests_oauthlib import OAuth2Session
# To init the site oauth2 sessions
from oauthlib.oauth2 import BackendApplicationClient
# For client_credential objects
from requests.auth import HTTPBasicAuth


class Site(object):
    def __init__(self, client_credentials: list, timeout_sec: int, limit: int):
        self.balancer = SiteBalancer(client_credentials, timeout_sec, limit)
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

    def get_soup(self, url: str, pause=False, pause_time=None):
        # handle delay if set to spread out requests
        if pause:
            self.pause(pause_time)

        # TODO: Set this up to wait on a signal from a timer thread so that it isn't a busy wait
        # get the next id to use or wait until one is ready
        while not self.balancer.is_ready():
            sleep(1)
            print(":(")

        client_credential = next(self.balancer)

        # grab some questions, need to set verify to false otherwise will get an error with the tls certificate
        try:
            response = client_credential.oauth_session.get(url)
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


class Oauth2ClientCredential(object):
    """
    Example of backend workflow from https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html

    from oauthlib.oauth2 import BackendApplicationClient
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', client_id=client_id,
        client_secret=client_secret)

    If your provider requires that you pass auth credentials in a Basic Auth header, you can do this instead:

    from oauthlib.oauth2 import BackendApplicationClient
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', auth=auth)

    r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    """

    def __init__(self, client_auth: HTTPBasicAuth, token_url: str):
        self.auth = client_auth
        self.client = BackendApplicationClient(client_id=client_auth.username)
        self.oauth_session = OAuth2Session(client=self.client)
        self.token = self.oauth_session.fetch_token(token_url=token_url, auth=self.auth)

    def __lt__(self, other):
        if not isinstance(other, Oauth2ClientCredential):
            raise TypeError
        return self.auth.username < other.auth.username
