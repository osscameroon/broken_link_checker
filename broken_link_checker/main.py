#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from checker import Checker
from notifier import Notifier

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('HOST', help='Eg: http://example.com')
    parser.add_argument('-d', '--delay', type=float, default=1,
                        help='It represent the delay between each request')
    parser.add_argument('-s', '--sender', type=str, default=None,
                        help='It represent the email used to send the report')
    parser.add_argument('-p', '--password', type=str, default=None,
                        help='It represent the password used for the login')
    parser.add_argument('-S', '--smtp_server', type=str, default=None,
                        help='It represent the email server used to send the report')
    parser.add_argument('-r', '--recipient', type=str, default=None,
                        help='It represent the email where send the report')
    args = parser.parse_args()

    # We initialize the checker
    checker = Checker(
        args.HOST,
        delay=args.delay,
    )

    # We initialize the notifier
    notifier = Notifier(
        smtp_server=args.smtp_server,
        username=args.sender,
        password=args.password,
    )

    # We start the checker
    checker.run()

    # We verify if the email notifier is configured
    # and broken links are found
    if args.smtp_server and checker.broken_url:
        # We build the report
        msg = f"Hello, your website <{args.HOST}>"\
            f" contains {len(checker.broken_url)} broken links:\n"
        msg += '\n'.join(checker.broken_url)

        # We notify the admin
        print(args.recipient)
        notifier.send(subject='Broken links found', body=msg, recipient=args.recipient)
    else:
        print('Broken links:\n' + '\n'.join(checker.broken_url))
