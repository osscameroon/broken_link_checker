#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module of the Broken Link Checker."""


from argparse import ArgumentParser
from checker import Checker
from notifier import Notifier
from configparser import ConfigParser
import sys
import logging
import threading

logging.basicConfig(
    filename='logging.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main(args):
    """Do something."""
    # parse values from a configuration file if provided and use those as the
    # default values for the argparse arguments
    config_argparse = ArgumentParser(add_help=False)
    config_argparse.add_argument('-c', '--config-file',
                                 help='path to configuration file')
    config_argparse.add_argument('-D', '--debug',
                                 help='enable the debug mode',
                                 type=bool,
                                 default=False)
    config_args, _ = config_argparse.parse_known_args(args)

    defaults = {
        "host": None,
        "delay": None,
        "sender": None,
        "password": None,
        "smtp_server": None,
        "recipient": None,
    }

    if not config_args.debug:
        logging.disable(logging.CRITICAL)

    if config_args.config_file:
        logging.info('Loading of the config file...')
        try:
            config_parser = ConfigParser()
            with open(config_args.config_file) as f:
                config_parser.read_file(f)
            config_parser.read(config_args.config_file)
        except OSError as err:
            print(err)
            sys.exit(1)

        defaults.update(dict(config_parser.items('Checker')))
        defaults.update(dict(config_parser.items('Notifier')))

    # parse the program's main arguments using the dictionary of defaults and
    # the previous parsers as "parent' parsers
    parser = ArgumentParser(
        parents=[config_argparse])
    parser.set_defaults(**defaults)
    parser.add_argument('-H', '--host', type=str,
                        help='Eg: http://example.com')
    parser.add_argument('-d', '--delay', type=float,
                        help='It represent the delay between each request')
    parser.add_argument('-s', '--sender', type=str,
                        help='It represent the email used to send the report')
    parser.add_argument('-p', '--password', type=str,
                        help='It represent the password used for the login')
    parser.add_argument('-S', '--smtp_server', type=str,
                        help='It represent the email server used to send the report')
    parser.add_argument('-r', '--recipient', type=str,
                        help='It represent the email where send the report')
    args = parser.parse_args()

    # We verify the dependency
    if not args.host:
        parser.error('host is required')
    elif (args.sender or args.password or args.smtp_server or args.recipient)\
            and not (args.sender and args.password and args.smtp_server and args.recipient):
        parser.error('bad configuration of the notifier')
    else:
        pass

    checker_threads = []
    broken_url = {}

    for target in args.host.split(','):
        # We initialize the checker
        checker = Checker(
            target,
            delay=args.delay if args.delay is not None else 1.0,
        )
        # We config the shared dict
        broken_url[target] = {}
        checker.broken_url = broken_url[target]

        checker_threads.append(threading.Thread(target=checker.run))
        checker_threads[-1].daemon = True

    # We initialize the notifier
    notifier = Notifier(
        smtp_server=args.smtp_server,
        username=args.sender,
        password=args.password,
    )

    # We start the checkers
    for thread in checker_threads:
        logging.info('Checking of %s' % args.host)
        thread.start()

    # We wait for the completion
    [thread.join() for thread in checker_threads]

    # We build the report
    msg = 'Hello, the report of the broken link checker is ready.\n'
    for target in broken_url:
        msg += f"Report of {target}:\n"
        if broken_url[target]:
            for data in broken_url[target].items():
                msg += ': '.join(data) + '\n'
        else:
            msg += "No broken url found\n"

    # We verify if the email notifier is configured
    if args.smtp_server:
        # We notify the admin
        logging.info('Sending of the report to %s...' % args.recipient)
        notifier.send(subject='Broken links found', body=msg, recipient=args.recipient)
    else:
        print(msg)


if __name__ == '__main__':
    main(sys.argv[1:])
