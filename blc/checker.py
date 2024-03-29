#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checker module."""

import requests
import requests_html
from urllib.parse import urljoin
import time
import logging
import re
import difflib
import html

# We change the log level for requests’s logger
logging.getLogger("requests_html").setLevel(logging.WARNING)


class Checker:
    """
    Check if an broken URL is present inside a website.

    :host represent the website to check
    :delay represent the delay between each request
    :deep_scan enable the check of foreign url
        just verify the availability of these URL
    """

    def __init__(self, host: str, delay: int = 1, deep_scan: bool = False,
                 browser_sleep: float = None):
        """Init the checker."""
        # We config the logger
        self.logging = logging.getLogger(f'checker({host})')
        self.logging.setLevel(logging.DEBUG)
        self.logging.debug('We initialize the checker for %s' % host)

        # We config the connection
        self.conn = requests_html.HTMLSession()
        self.conn.headers.update({
            "User-Agent": "BrokenLinkChecker/1.0",
        })
        self.timeout = 2
        self.browser_sleep = browser_sleep
        self.max_download_size = 1048576  # 1MB

        self.host = host

        # Delay between each request
        self.delay = delay

        # Shallow scan of foreign url
        self.deep_scan = deep_scan

        # Will represent the list of checked URL
        self.urls = {
            host: {
                'parent': [],
                'url': None,
                'result': None,
                'check_time': None

            }
        }

        # Will represent the previous webpage content
        self.prev_data = ''

        # Represent a regex to find all link URLs inside an text source
        self.REGEX_TEXT_URL = re.compile(
            r"href=[\'\"](.*?)[\'\"]"
            r"|href=(.*?)[ |>]"
            r"|<link>(.*?)</link>"
            r"|<url>(.*?)</url>"
            r"|src=[\'\"](.*?)[\'\"]"
            r"|src=(.*?)[ |>]"
            # Ref: http://www.regexguru.com/2008/11/
            #   detecting-urls-in-a-block-of-text/
            r"|\b(https?://[-A-Z0-9+&@#/%?=~_|!:,.;]*[A-Z0-9+&@#/%=~_|])",
            re.IGNORECASE
        )

        self.REGEX_CLEAN_URL = re.compile(
            r"[-A-Z0-9+&@#/%?=~_|!:,.;]*",
            re.IGNORECASE
        )

        # Regex to verify the content type
        self.REGEX_CONTENT_TYPE = re.compile(
            r"text/(xml|html)"
            r"|application/(rss|xml)",
            re.IGNORECASE
        )

    def is_same_host(self, url):
        """
        Verify if the url belongs the host.

        :url the url to verify
        """
        host = requests.utils.urlparse(self.host)
        url = requests.utils.urlparse(url)

        if not url.scheme:
            return True
        elif (
            url.scheme == host.scheme
                and url.netloc == host.netloc
                and url.port == host.port):
            return True
        else:
            return False

    def check(self, url: str) -> requests_html.HTMLResponse:
        """
        Verify if a link is broken of not.

        :url represent the URL to check
        """
        # We verify the URL is already checked
        if self.urls[url]['result']:
            return None

        self.logging.info('Checking of %s...' % url)

        # We make a connection
        try:
            if self.is_same_host(url):
                response = self.conn.get(url, timeout=self.timeout,
                                         stream=True)
            else:
                response = self.conn.head(url, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            self.urls[url]['result'] = False, None, "Timeout!"
        except requests.exceptions.ConnectionError:
            self.urls[url]['result'] = False, None, "Connection aborted!"
        except requests.exceptions.TooManyRedirects:
            self.urls[url]['result'] = False, None, "Too many redirection!"
        else:
            # We verify the response status
            # 2xx stand for request was successfully completed
            if response.ok:
                self.urls[url]['result'] = (
                    True, response.status_code, response.reason)
                return response if self.is_same_host(url) else None
            else:
                self.urls[url]['result'] = (
                    False, response.status_code, response.reason)

                self.logging.warning(
                    '%s maybe broken because status code: %i' %
                    (url, response.status_code)
                )
                return None

    def update_list(self, response: requests_html.HTMLResponse) -> None:
        """
        Update the list of URL to checked
         in function of the URL get in a webpage.

        :response represent the http response who contains the data to analyze
        """
        # We verify if the content is a webpage
        if self.REGEX_CONTENT_TYPE.match(response.headers['Content-Type']):
            self.logging.debug('Getting of the webpage...')
            data = None

            # We execute the js script
            if self.browser_sleep is not None:
                try:
                    # We wait to load the js and in case of connection latency
                    response.html.render(
                        timeout=self.timeout,
                        sleep=self.browser_sleep)
                    data = response.html.html
                except (AttributeError, requests_html.etree.ParserError):
                    pass
                except requests_html.pyppeteer.errors.TimeoutError:
                    pass

            if data is None:
                # we read fixed bytes by precaution
                response.raw.decode_content = True
                data = response.raw.read(self.max_download_size)
                self.logging.debug('Decoding of data...')
                data = data.decode()

            # We verify if we are not already got this content
            #   in the previous request
            if (difflib.SequenceMatcher(None, data, self.prev_data)
                    .ratio() > 0.9):
                self.logging.warning(
                    response.url + ''
                    ' skipped because content similar'
                    ' at +90% with the previous URL.'
                )
                return
            else:
                self.prev_data = data

            self.logging.debug('Getting of the URLs...')

            # Some url can be escape by the browser
            data = html.unescape(data)

            # We build a list of cleaned links
            urls = [
                self.REGEX_CLEAN_URL.findall(ii)[0]
                for i in self.REGEX_TEXT_URL.findall(data)
                if i for ii in i if ii
            ]

            # In this step, we have two possibilities
            # 1. The URL belongs to the HOST
            # 1.1. The URL is absolute
            # 1.2. The URL is relative
            # 2. The URL don't belongs to the HOST
            for url in urls:

                origin_url = url

                # 1.1 and 1.2
                if self.is_same_host(url):
                    # 1.2
                    if not requests.utils.parse_url(url).scheme:
                        # We verify if the URL is different of the parent
                        if not url.startswith('#') and not url.startswith('?'):
                            # We build the absolute URL
                            url = urljoin(response.url, url)
                        else:
                            # Since this URL is relative
                            # maybe it is not different of the parent
                            # Eg: /home and /home#
                            continue
                    else:
                        # 1.1
                        pass
                # 2
                elif self.deep_scan:
                    data = requests.utils.urlparse(url)
                    # Just the HTTP and HTTPS scheme will be allowed
                    if data.scheme in ['http', 'https']:
                        pass
                    else:
                        continue
                else:
                    continue

                # Except if the deep_scan is enable
                # At this point, the URL belongs to the HOST
                # We verify that the URL is neither already added nor checked
                if url in self.urls:
                    if (url != response.url
                            and response.url not in self.urls[url]['parent']):
                        self.urls[url]['parent'].append(response.url)
                elif url != response.url:
                    self.logging.debug('Add the URL %s' % url)
                    self.urls[url] = {
                        'parent': [response.url],
                        'url': origin_url,
                        'result': None,
                        'check_time': None

                    }
                else:
                    continue

            # We close the connection
            response.close()
        else:
            self.logging.warning(
                '%s ignored because Content-Type %s' %
                (response.url, response.headers['Content-Type'])
            )

    def run(self) -> None:
        """Run the checker."""
        # We check while we have an URL unchecked
        while 1:
            url_to_check = [u for u in self.urls if not self.urls[u]['result']]

            if not url_to_check:
                break

            while url_to_check:
                url = url_to_check.pop(0)
                self.urls[url]['check_time'] = time.time()
                response = self.check(url)
                if response:
                    self.update_list(response)
                self.urls[url]['check_time'] = (
                    time.time() - self.urls[url]['check_time'])
                time.sleep(self.delay)
