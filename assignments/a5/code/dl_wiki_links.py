from wiki_helpers import *
from concurrent.futures import ProcessPoolExecutor
from requests_futures.sessions import FuturesSession
import requests
import re

useragents = [
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Linux; Ubuntu 14.04) AppleWebKit/537.36 Chromium/35.0.1870.2 Safari/537.36'
]


def dl_wiki_links():
    link_df = get_link_df()
    di = domain_info(link_df)
    result = {}
    temp = []
    num = re.compile('^(?:(?:www\.)|(?:http://)|(?:https://))?(?:[0-9]{1,3}\.){3}.+$')
    c = 0
    processed = 0
    with FuturesSession(session=requests.Session(), executor=ProcessPoolExecutor(max_workers=10)) as session:
        for href in di.href.unique():
            if not href.startswith('http') and not href.startswith('https'):
                href = '%s%s' % ('http://', href)
            if num.match(href) is not None:
                result[href] = -2
                continue
            temp.append(href)
            if len(temp) >= 1000:
                pending = []
                for url in temp:
                    result[url] = -1
                    pending.append(session.head(url, headers={'User-Agent': useragents[c]}, timeout=3.0))
                    c += 1
                    if c == 3:
                        c = 0
                for future in pending:
                    try:
                        response = future.result()
                        url = response.url
                        scode = response.status_code
                        result[url] = scode
                    except Exception as e:
                        one = 1
                    processed += 1
                    if processed % 1000 == 0:
                        print(processed)
                temp.clear()

    print('outise the with')
    dump_pickle(result, wsmall_latest_nwl_status)
