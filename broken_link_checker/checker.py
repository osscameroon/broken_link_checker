#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checker module."""

import urllib3
from urllib3.util import Timeout, parse_url, Url
from urllib.parse import urljoin
import time
import logging
import re

# We change the log level for urllib3’s logger
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Checker:
    """
    Check if an broken URL is present inside a website.

    :host represent the website to check
    :delay represent the delay between each request
    """

    def __init__(self, host: str, delay: int = 1):
        """Init the checker."""
        # We config the logger
        self.logging = logging.getLogger('checker')
        self.logging.setLevel(logging.DEBUG)
        self.logging.debug('We initialize the checker for %s' % host)

        # We config the connection
        self.conn = urllib3.connection_from_url(
            host,
            # We config the timeout
            timeout=Timeout(connect=2.0, read=7.0),
            headers=urllib3.util.make_headers(
                user_agent="BrokenLinkChecker/1.0",
                keep_alive=True
            ),
            # We config the max number of connection
            maxsize=1,
        )

        # Delay between each request
        self.delay = delay

        # Will represent the list of URL to check
        self.url_to_check = ['/']

        # Will represent the list of checked URL
        self.checked_url = []

        # Will represent the list of broken URL
        self.broken_url = {}

        # Represent a regex to find all link URLs inside an text source
        self.REGEX_TEXT_URL = re.compile(
            r"href=[\'\"](.*?)[\'\"]"
            r"|href=(.*?)[ |>]"
            r"|<link>(.*?)</link>"
            r"|<url>(.*?)</url>"
            r"|src=[\'\"](.*?)[\'\"]"
            r"|src=(.*?)[ |>]"
            # Ref: http://www.regexguru.com/2008/11/detecting-urls-in-a-block-of-text/
            r"|\b(https?://[-A-Z0-9+&@#/%?=~_|!:,.;]*[A-Z0-9+&@#/%=~_|])",
            re.IGNORECASE
        )

        # Regex to verify the content type
        self.REGEX_CONTENT_TYPE = re.compile(
            r"text/(xml|html)"
            r"|application/(rss|xml)",
            re.IGNORECASE
        )

    def check(self, url: str) -> urllib3.response.HTTPResponse | None:
        """
        Verify if a link is broken of not.

        :url represent the URL to check
        """
        # We get only the path part
        url = parse_url(url).path or '/'

        # We verify the URL is already checked
        if url in self.checked_url:
            return None

        self.logging.info('Checking of %s...' % url)

        # We mark the URL checked
        self.checked_url.append(url)

        # We make a connection
        response = self.conn.request(
            'GET',
            url,
            preload_content=False
        )

        # We verify the response status
        if response.status == 200:
            return response
        else:
            self.broken_url[url] = response.reason
            self.logging.warning(
                '%s maybe broken because status code: %i' %
                (url, response.status)
            )
            return None

    def update_list(self, response: urllib3.response.HTTPResponse) -> None:
        """
        Update the list of URL to checked in function of the URL get in a webpage.

        :response represent the http response who contains the data to analyze
        """
        # We verify if the content is a webpage
        if self.REGEX_CONTENT_TYPE.match(response.headers['Content-Type']):
            self.logging.debug('Getting of the webpage...')
            # we read max 2**20 bytes by precaution
            data = response.read(1048576)
            self.logging.debug('Decoding of data...')
            data = data.decode()
            self.logging.debug('Getting of the URLs...')

            matches = self.REGEX_TEXT_URL.findall(data)

            # In this step, we have two possibilities
            # 1. The URL belongs to the HOST
            # 1.1. The URL is absolute
            # 1.2. The URL is relative
            # 2. The URL don't belongs to the HOST
            for match in matches:
                # We get the URL match
                url = [i for i in match if i][0]

                # 1.1
                if self.conn.is_same_host(url):
                    pass
                # 1.2 and 2
                else:
                    # 1.2
                    if not urllib3.util.parse_url(url).scheme:
                        # We verify if the URL is different of the parent
                        if not url.startswith('#') and not url.startswith('?'):
                            # We build the absolute URL
                            url = urljoin(response._request_url, url)
                        else:
                            # Since this URL is relative
                            # maybe it is not different of the parent
                            # Eg: /home and /home#
                            continue
                    # 2
                    else:
                        self.logging.warning('the URL %s don\'t belong the host' % url)
                        continue

                # At this point, the URL belongs to the HOST
                # We verify that the URL is neither already added nor checked
                if url not in self.url_to_check \
                    and url not in self.checked_url \
                        and url != response._request_url:
                    self.logging.debug('Add the URL %s' % url)
                    self.url_to_check.append(url)
                else:
                    continue

            # We close the connection
            response.close()
        else:
            self.logging.warning(
                '%s ignored because Content-Type %s' %
                (response._request_url, response.headers['Content-Type'])
            )

    def run(self) -> None:
        """Run the checker."""
        # We check while we have an URL unchecked
        while (self.url_to_check):
            response = self.check(self.url_to_check.pop(0))
            if response:
                self.update_list(response)
            time.sleep(self.delay)
