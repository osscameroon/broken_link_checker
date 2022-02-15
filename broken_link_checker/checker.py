#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib3
from urllib3.util import Timeout, parse_url, Url
import time
import logging
import re

# We change the log level for urllib3’s logger
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Checker:
    """
        This module permit to check if an broken URL
         is present inside a website.
        :host represent the website to check
    """
    def __init__(self, host: str, delay: int = 1):
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
        self.broken_url = []

        # Represent a regex to find all link URLs inside an HTML source
        self.REGEX_HTML_URL = re.compile(
            r"href=[\'\"](.*?)[\'\"]"
            r"|href=(.*?)[ |>]"
            r"|<link>(.*?)</link>",
            re.IGNORECASE
        )

        # Regex to verify the content type
        self.REGEX_CONTENT_TYPE = re.compile(
            r"text/[xml|html]",
            re.IGNORECASE
        )

    """
        This method verify if a link is broken of not
        If not broken and is webpage, update the list of URL to check with the
        children link of this link

        :url represent the URL to check
    """
    def check(self, url: str) -> None:
        # We get only the path part
        url = parse_url(url).path or '/'

        # We verify the URL is already checked
        if url in self.checked_url:
            return

        print('[INFO] Checking of %s...' % url)

        # We make a connection
        response = self.conn.request(
            'GET',
            url,
            preload_content=False
        )

        # We verify the response status
        if response.status == 200:
            # We verify if the content is a webpage
            if self.REGEX_CONTENT_TYPE.match(response.headers['Content-Type']):
                # print('[DEBUG] Getting of the webpage...')
                # we read max 2**20 bytes by precaution
                data = response.read(1048576)
                # print('[DEBUG] Getting of the URLs...')
                # We update the list of URL to check
                self.update_list(url, data.decode())

                # We close the connection
                response.close()
            else:
                print(
                    '[WARNING] %s ignored because Content-Type %s' %
                    (url, response.headers['Content-Type'])
                )
        else:
            self.broken_url.append(url)
            print(
                '[WARNING] %s maybe broken because status code: %i' %
                (url, response.status)
            )

        # We mark the URL checked
        self.checked_url.append(url)

    """
        This method update the list of URL to checked in function
         of the URL get in a webpage.
        :parent_url represent the parent of these URL
        It need for the conversion of relative URL to absolute URL
        :data represent the HTML source of the parent URL
    """
    def update_list(self, parent_url: str, data: str) -> None:
        matches = self.REGEX_HTML_URL.findall(data)

        # In this step, we have two possibilities
        # 1. The URL belongs to the HOST
        # 1.1. The URL is absolute
        # 1.2. The URL is relative
        # 2. The URL don't belongs to the HOST
        for match in matches:
            # We get the URL match
            url = match[0] or match[1] or match[2]

            # 1.1
            if self.conn.is_same_host(url):
                # We verify that the URL is not already added nor checked
                if url not in self.url_to_check \
                    and url not in self.checked_url \
                        and url != parent_url:
                    print('[INFO] Add the URL %s' % url)
                    self.url_to_check.append(url)
            # 1.2 and 2
            else:
                # 1.2
                if not urllib3.util.parse_url(url).scheme:
                    # We build the absolute URL
                    url = '/' + parent_url.strip('/') + '/' + url.strip('/')
                    # We verify that the URL is not already added nor checked
                    if url not in self.url_to_check \
                        and url not in self.checked_url \
                            and url != parent_url:
                        self.url_to_check.append(url)
                        print('[INFO] Add the URL %s' % url)
                # 2
                else:
                    # print('[WARNING] the URL %s don\'t belong the host'%url)
                    pass

    """
        This method run the checker
    """
    def run(self) -> None:
        # We check while we have an URL unchecked
        while (self.url_to_check):
            self.check(self.url_to_check.pop(0))
            time.sleep(self.delay)
