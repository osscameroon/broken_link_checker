"""
main module of blc
"""
import json
from urllib.parse import urljoin, urlparse
import bs4
from requests.models import Response
from requests_html import HTMLSession

import colorama
from bs4 import BeautifulSoup

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
CYAN = colorama.Fore.CYAN
RED = colorama.Fore.RED
WHITE = colorama.Fore.WHITE

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
good_urls = set()
bad_urls = set()

total_urls_visited = 0


def is_valid(url: str):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def request_get(url: str) -> Response:
    """
    The simple requests get function
    """
    # initialize an HTTP session
    session = HTMLSession()
    # make HTTP request & retrieve response
    response = session.get(url)
    # execute Javascript
    try:
        getattr(response, 'html').render()
    except Exception:
        pass

    return response


def get_links_from_hrefs(
    soup: bs4.BeautifulSoup,
    domain_name: str,
    urls: set
) -> set:
    """
    Extract from soup object, urls from href
    """
    for a_tag in soup.findAll('a'):
        href = a_tag.attrs.get('href')
        if href == '' or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = (
            f'{parsed_href.scheme}://{parsed_href.netloc}{parsed_href.path}'
        )
        if 'mailto://' in href:
            # For a mail link
            print(f'{CYAN}[*] Mail link not checked : {href}{RESET}')
            continue
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f'   {GRAY}[!] External link: {href}{RESET}')
                external_urls.add(href)
            continue
        print(f'   {WHITE}[*] Internal link: {href}{RESET}')
        urls.add(href)
        internal_urls.add(href)

        urls = urls.union(get_all_website_links(href))

    return urls


def get_all_website_links(url: str) -> set:
    """
    Returns all URLs that is found on `url` in which
    it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    try:
        resp = request_get(url)
        if '40' in str(resp.status_code):
            bad_urls.add(json.dumps({
                'reason': resp.status_code,
                'url': url
            }))
            print(
                f'{RED}[✗] unreacheable: ({resp.status_code}) <> {url}{RESET}'
            )
            return urls
    except ConnectionError:
        bad_urls.add(json.dumps({
            'reason': 404,
            'url': url
        }))
        print(
            f'{RED}[✗] unreacheable: (404) <> {url}{RESET}'
        )
        return urls

    print(f'{GREEN}[✓] <> {url}{RESET}')
    good_urls.add(url)
    soup = BeautifulSoup(getattr(resp, 'html').html, 'html.parser')
    urls = get_links_from_hrefs(soup, domain_name, urls)

    return urls


def crawl(url: str, max_urls: int = 30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls`
    global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


def generate_report():
    """
    This function will crawl the website and print links report
    on the stdout and also inside the final json file
    """
    crawl(url, max_urls=max_urls)
    print('[+] Internal links:', len(internal_urls))
    print('[+] External links:', len(external_urls))
    print('[+] Bad-links/Internal-links:', len(bad_urls))
    print('[+] Good-links/Internal-links:', len(good_urls))
    print('[+] Total URLs:', len(external_urls) + len(internal_urls))

    domain_name = urlparse(url).netloc

    report = {
        'external-urls': list(external_urls),
        'internal-urls': list(internal_urls),
        'good-urls': list(good_urls),
        'bad-urls': list(bad_urls)
    }

    # save the internal links to a file
    with open(f'{domain_name}_report.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=3))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='Link Extractor Tool with Python'
    )
    parser.add_argument('url', help='The URL to extract links from.')
    parser.add_argument(
        '-m',
        '--max-urls',
        help='Number of max URLs to crawl, default is 30.',
        default=30,
        type=int,
    )

    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls
    generate_report()
