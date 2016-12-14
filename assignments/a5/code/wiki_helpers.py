import os
import requests
import re
import pandas as pd
import numpy as np
import tldextract
from collections import defaultdict, Counter
from urllib.parse import quote
from contextClasses import BeautifulSoupFromFile
from wiki_vocab import vocab_small_new
from util import read_pickle, dump_pickle

base = 'https://en.wikipedia.org/wiki/%s'
wiki_http_link = re.compile('^http(?:s)?:.+$')
match_end = re.compile('.+(_[0-9a-z]{4}\.html)$')

tidied_uirs = 'pickled/titdy_uris.pickle'
wsmall_statues = 'pickled/wsmall_statuses.pickle'

wsmall_latest_p = 'wiki_small_latest/%s'

wsmall_latest_links = 'output_files/wsmall_latest.csv'
wsmall_latest_linkdf = 'pickled/wsmall_nlinks.pickle'
wsmall_latest_path = 'wiki_small_latest/%s'
wsmall_latest_webarchive = 'pickled/wsmall_nweba.pickle'
wsmall_latest_no_wlink = 'pickled/wsmall_no_wiki_links.pickle'
wsmall_latest_no_wlinkd = 'pickled/wsmall_no_wiki_linkswd.pickle'
wsmall_latest_nwl_status = 'pickled/wsmall_no_wiki_links_status.pickle'

wsmall_old_links = 'output_files/wsmall_old_links.csv'
wsmall_old_linkdf = 'pickled/wsmall_old_linksdf.pickle'

archiving_sites = ['http://www.britishnewspaperarchive.co.uk', 'http://webarchive.loc.gov',
                   'https://archive.org/', 'http://www.webcitation.org/',
                   'http://webarchive.nationalarchives.gov.uk', 'https://web.archive', 'http://www.archive.today']


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
                uri = base % tidy['unquoted']
                r = session.get(uri)
                scode = r.status_code
                print(uri, scode)
                statuses[tidy['original']] = scode
                if scode == 200:
                    with open('wiki_small_latest/%s' % tidy['original'].replace('\'',''), 'w') as out:
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


def extract_links_count_vocab(wstatues):
    if not os.path.exists(wsmall_latest_links):
        with open(wsmall_latest_links, 'w') as out:
            out.write('wsmall_file,href\n')
            for o, scode in filter(lambda x: x[1] == 200, wstatues.items()):
                with BeautifulSoupFromFile(wsmall_latest_path % o, 'lxml') as soup:
                    all_a = soup.find_all('a', href=True)
                    for a in filter(a_filter, all_a):
                        out.write('%s,%s\n' % (o, a['href']))
        vocab_small_new()


def extract_links_old(wl):
    if not os.path.exists(wsmall_old_links):
        with open(wsmall_old_links, 'w') as out:
            out.write('wsmall_file,href\n')
            for wp in wl:
                with BeautifulSoupFromFile(wp, 'lxml') as soup:
                    all_a = soup.find_all('a', href=True)
                    for a in filter(a_filter, all_a):
                        href = a['href']
                        if href.startswith('../../../../articles') or href.startswith('../../../../'):
                            href = href[href.rfind('/') + 1:]
                            m = match_end.findall(href)
                            if len(m) > 0:
                                href = href.replace(m[0], '')
                            else:
                                href = href.replace('.html', '')
                        elif href.startswith('http') and '../../../../articles' in href:
                            # print(href[href.rfind('/')+1:])
                            href = href[href.rfind('/') + 1:]
                            m = match_end.findall(href)
                            if len(m) > 0:
                                href = href.replace(m[0], '')
                            else:
                                href = href.replace('.html', '')
                        original = os.path.basename(wp)
                        m = match_end.findall(original)
                        # print(m)
                        if len(m) > 0:
                            p_name = original.replace(m[0], '')
                        else:
                            p_name = original.replace('.html', '')
                        out.write('%s,%s\n' % (p_name, href))


def get_oldl_df():
    if not os.path.exists(wsmall_old_linkdf):
        names = ['wsmall_file', 'href']
        ldf = pd.read_csv(wsmall_old_links, sep=',', names=names)
        dump_pickle(ldf, wsmall_old_linkdf)
        return ldf
    else:
        return read_pickle(wsmall_old_linkdf)


def get_link_df():
    if not os.path.exists(wsmall_latest_linkdf):
        names = ['wsmall_file', 'href']
        ldf = pd.read_csv(wsmall_latest_links, sep=',', names=names)
        dump_pickle(ldf, wsmall_latest_linkdf)
        return ldf
    else:
        return read_pickle(wsmall_latest_linkdf)


def check_webarchive(ldf):
    if not os.path.exists(wsmall_latest_webarchive):
        archive_sites = []
        for archive_site in archiving_sites:
            archive_sites.append(ldf[ldf.href.str.startswith(archive_site)])
        about_wba = pd.concat(archive_sites)
        dump_pickle(about_wba, wsmall_latest_webarchive)
        return about_wba
    else:
        return read_pickle(wsmall_latest_webarchive)


def front_slash_nuke(r):
    if r.startswith('//'):
        return r.lstrip('//')
    return r


def domain_getter(href):
    d = tldextract.extract(href).registered_domain
    if d == '':
        return np.nan
    return d


def domain_info(ldf=None):
    if not os.path.exists(wsmall_latest_no_wlink):
        no_wlinks = ldf[ldf.href.str.contains(r'(www)|(http)')][~ldf.href.str.contains('wiki')]
        no_wlinks['href'] = no_wlinks['href'].apply(front_slash_nuke)
        dump_pickle(no_wlinks, wsmall_latest_no_wlink)
        if not os.path.exists(wsmall_latest_no_wlinkd):
            no_wlinks['domain'] = no_wlinks.href.map(domain_getter)
            dump_pickle(no_wlinks, wsmall_latest_no_wlinkd)
    else:
        no_wlinks = read_pickle(wsmall_latest_no_wlinkd)

    return no_wlinks


class LinkDict(dict):
    def __missing__(self, key):
        res = self[key] = 0
        return res


def compute_old_wsmall_links():
    if not os.path.exists('pickled/wsmallo_outl_temp.pickle'):
        old_link_df = get_oldl_df()
        out = defaultdict(LinkDict)
        for owfile in old_link_df.wsmall_file.unique():
            owdf = old_link_df[old_link_df.wsmall_file == owfile]
            links_to = old_link_df[old_link_df.wsmall_file.isin(owdf.href)]
            links_to_other = owdf[~owdf.href.isin(links_to.href)]
            out[owfile]['outlink_wsmall'] += links_to.wsmall_file.unique().size
            out[owfile]['outlink_other'] += links_to_other.wsmall_file.unique().size
            out[owfile]['total_outlinks'] += out[owfile]['outlink_wsmall'] + out[owfile]['outlink_other']
            for other in links_to.wsmall_file.unique():
                out[other]['inlink'] += 1
        dump_pickle(out, 'pickled/wsmallo_outl_temp.pickle')
    else:
        out = read_pickle('pickled/wsmallo_outl_temp.pickle')
    return out


def old_wsmall_lstats_df():
    if not os.path.exists('pickled/wsmallo_outl_stats.pickle'):
        old_wsmall_links = compute_old_wsmall_links()
        it = {'wsmall': [], 'outlink_wsmall': [], 'outlink_other': [], 'total_outlinks': [], 'inlinks': []}
        for name in old_wsmall_links.keys():
            it['wsmall'].append(name)
            it['outlink_wsmall'].append(old_wsmall_links[name]['outlink_wsmall'])
            it['outlink_other'].append(old_wsmall_links[name]['outlink_other'])
            it['total_outlinks'].append(old_wsmall_links[name]['total_outlinks'])
            it['inlinks'].append(old_wsmall_links[name]['inlink'])
        lstats_df = pd.DataFrame(it)
        dump_pickle(lstats_df, 'pickled/wsmallo_outl_stats.pickle')
    else:
        lstats_df = read_pickle('pickled/wsmallo_outl_stats.pickle')

    return lstats_df
