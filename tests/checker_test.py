#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit Test of the module checker."""

import unittest
from blc.checker import Checker


class CheckerTest(unittest.TestCase):
    """Unit Test of the module checker."""

    def test_regex_with_html(self):
        """Test for the html source."""
        checker = Checker('localhost')

        with open('tests/data.html', 'r') as f:
            self.assertEqual(
                len([
                    i for i in checker.REGEX_TEXT_URL.findall(
                        f.read()
                    ) if any(i)
                ]),
                14
            )

        with open('tests/data2.html', 'r') as f:
            self.assertEqual(
                len([
                    i for i in checker.REGEX_TEXT_URL.findall(
                        f.read()
                    ) if any(i)
                ]),
                24
            )

    def test_regex_with_xml(self):
        """Test for the rss source."""
        checker = Checker('localhost')

        with open('tests/data.rss', 'r') as f:
            self.assertEqual(
                len([
                    i for i in checker.REGEX_TEXT_URL.findall(
                        f.read()
                    ) if any(i)
                ]),
                3
            )

    def test_update_list(self):
        """Test for the method update_list."""
        with open('tests/data.html', 'rb') as f1:
            with open('tests/data2.html', 'rb') as f2:
                with open('tests/data.rss', 'rb') as f3:
                    data = f1.read() + f2.read() + f3.read()

        class Response:
            headers = {'Content-Type': 'text/html'}
            url = 'http://localhost/'

            class raw:
                def read(x):
                    return data

            def close():
                pass

        # without deep mode
        checker = Checker(Response.url)
        checker.update_list(Response)

        self.assertEqual(len(checker.url_to_check), 18)

        # with deep mode
        checker = Checker('localhost', deep_scan=True)
        checker.update_list(Response)
        self.assertEqual(len(checker.url_to_check), 36)
