from collections import defaultdict
from util import read_pickle, dump_pickle
from requests import request, sessions
import urllib3
from urllib.parse import unquote, quote
import os
import re
import requests
from wiki_vocab import *
from contextClasses import BeautifulSoupFromFile

base = 'https://en.wikipedia.org/wiki/%s'
match_end = re.compile('.+(_[0-9a-z]{4}\.html)$')

tidied_uirs = 'pickled/titdy_uris.pickle'
wsmall_statues = 'pickled/wsmall_statuses.pickle'


def tidy_uris(s_list):
    if not os.path.exists(tidied_uirs):
        t = []
        for w in s_list:
            original = os.path.basename(w)
            m = match_end.findall(original)
            if len(m) > 0:
                p_name = original.replace(m[0], '')
            else:
                p_name = original.replace('.html', '')
            t.append({
                'quoted': quote(p_name),
                'unquoted': p_name,
                'original': original
            })
        dump_pickle(t, tidied_uirs)
        return t
    else:
        return read_pickle(tidied_uirs)


def dl_pages(tidied_uris):
    if not os.path.exists(wsmall_statues):
        useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01'
        statuses = {}
        with requests.session() as session:
            session.headers.update({'User-Agent': useragent})
            for tidy in tidied_uris:
                print(tidy['unquoted'])
                uri = base % tidy['unquoted']
                r = session.get(uri)
                scode = r.status_code
                print(uri, scode)
                statuses[tidy['original']] = scode
                if scode == 200:
                    with open('wiki_small_latest/%s' % tidy['original'], 'w') as out:
                        out.write(r.text)
        dump_pickle(statuses, wsmall_statues)
        return statuses
    else:
        return read_pickle(wsmall_statues)


def a_filter(a):
    if a is None:
        return False
    else:
        return a['href'][0] != '#'


if __name__ == '__main__':
    small_list, _ = read_pickle('pickled/wsmall.pickle')
    tidy = tidy_uris(small_list)
    w_statues = dl_pages(tidy)
    out = []
    with open('output_files/wsmall_latest.csv', 'w') as out:
        out.write('wsmall_file,href\n')
        for o, scode in filter(lambda x: x[1] == 200, w_statues.items()):
            with BeautifulSoupFromFile('wiki_small_latest/%s' % o, 'lxml') as soup:
                all_a = soup.find_all('a', href=True)
                for a in filter(a_filter, all_a):
                    out.write('%s,%s\n' % (o, a['href']))
    vocab_small_new()
