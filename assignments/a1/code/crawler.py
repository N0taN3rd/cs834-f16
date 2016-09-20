#!/usr/bin/env python3
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import deque
from argparse import ArgumentParser
import time

reg_s = "((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|" + \
        "(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?" + \
        "\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)"
# my standard url regex found a while ago
url_re = re.compile(reg_s, re.IGNORECASE)

relative = re.compile("^(?!www\.|(?:http|ftp)s?://|[A-Za-z]:\\|//|(#[a-zA-Z0-9\-_]+)).*")


def gen_frontier(uri, session, q, seen):
    """
        Simplistic frontier generation function
        Download the current uri and if it resolves to a 200
        extract all the a elements.
        If we have seen the link contained in an href of the current
        a element skip it otherwise add it to our queue.
        A sanity check uri regex is utalized
        if it fails check if the uri is relative
        otherwise skip it
    """
    print('extracting links from %s'%uri)
    r = session.get(uri)  # type: requests.Response
    ctype = r.headers.get('Content-Type','why you no tell me').lower()
    if r.ok and 'text/html' in ctype:
        try:
            s = BeautifulSoup(r.text, 'html5lib')
        except:
            # just because if this fails there are problems
            s = BeautifulSoup(r.text,'htmllib')
        all_a = s.find_all('a', href=True)

        for link in map(lambda a: a['href'], all_a):
            if link not in seen:
                # print("extracting links from %s" % uri)
                if url_re.match(link):
                    print('found %s'%link)
                    q.append(link)
                    seen.add(link)
                else:
                    if relative.match(link):
                        print('found relative %s' % link)
                        fulllink = urljoin(r.url, link)
                        if fulllink not in seen :
                            q.append(fulllink)
                            seen.add(fulllink)
                    else:
                        print("The input uri %s failed to pass my regex " % link, relative)
    else:
        print("We have a link that does not resolves to an ok or is not text/html: %s, %d, %s" % (uri, r.status_code,ctype))


if __name__ == '__main__':
    parser = ArgumentParser(description="Single Threaded Crawler", prog='crawler', usage='%(prog)s [options]')
    parser.add_argument('-s', '--seed', help='seed to start crawling', type=str, default='http://cs.odu.edu/~mln')
    # ok I am adding this to the program as having worked with Heritrix an unbounded crawler will download the internet
    parser.add_argument('-hops', help='how many hops from the start should the crawler crawl', type=int,
                        default=2)
    args = parser.parse_args()
    useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01'
    hops = args.hops
    q = deque()
    # add the initial seed url to queue
    q.append(args.seed)
    # simple attempt at avoiding crawler traps i.e. links that reference the page containing them
    seen = set()

    with requests.Session() as session:
        session.headers.update({'User-Agent': useragent})
        uri = q.popleft()
        seen.add(uri)
        # extract all uris from the seed and add it to seen
        gen_frontier(uri, session, q, seen)
        # get the number of uris in the frontier for hop 1
        frontierCur = len(q)
        # continue crawling until we are at the last hop
        while hops > 0:
            time.sleep(5)
            uri = q.popleft()
            frontierCur -= 1
            # vist this uri and extract its uris
            gen_frontier(uri, session, q, seen)
            # when the frontier for the current hop has been exhausted
            if frontierCur == 0:
                # get the new frontier size
                frontierCur = len(q)
                # decrement hops as we are now one curHop+1 away from the seed uri
                hops -= 1
                print('we completed one hop. hops left=%d, next frontier size=%d' % (hops, frontierCur))
        # we are now at the last hop exhaust the queue
        print("printing uris at hope %d away from the seed"%args.hops)
        while True:
            try:
                uri = q.popleft()
                print('uri gotten from last hop'%uri)
            except IndexError:
                break

