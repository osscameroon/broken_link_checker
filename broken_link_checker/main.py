#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from checker import Checker

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('HOST', help='Eg: http://example.com')
    parser.add_argument('-d', '--delay', type=float, default=1,
                        help='It represent the delay between each request')
    args = parser.parse_args()

    # We start the checker
    Checker(
        args.HOST,
        delay=args.delay,
    ).run()