#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit Test of the module checker."""

import unittest
from broken_link_checker.checker import Checker


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
        checker = Checker('localhost')

        with open('tests/data.html', 'r') as f1:
            with open('tests/data2.html', 'r') as f2:
                with open('tests/data.rss', 'r') as f3:
                    data = f1.read() + f2.read() + f3.read()

        checker.update_list('/', data)
        self.assertEqual(len(checker.url_to_check), 18)
