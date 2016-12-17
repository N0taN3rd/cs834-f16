import os
import re
import requests
import pandas as pd
import numpy as np
import tldextract
import csv
from tabulate import tabulate
from concurrent.futures import ProcessPoolExecutor
from requests_futures.sessions import FuturesSession
from collections import defaultdict, Counter
from urllib.parse import quote
from contextClasses import BeautifulSoupFromFile
from wiki_vocab import vocab_small_new
from util import read_pickle, dump_pickle

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

size_compare = 'output_files/wsmall_sizes.csv'
status_csv = 'output_files/wsmalln_statuses.csv'
status2_csv = 'output_files/wsmalln_statuses2.csv'

useragents = [
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Linux; Ubuntu 14.04) AppleWebKit/537.36 Chromium/35.0.1870.2 Safari/537.36'
]

base = 'https://en.wikipedia.org/wiki/%s'
wiki_http_link = re.compile('^http(?:s)?:.+$')
match_end = re.compile('.+(_[0-9a-z]{4}\.html)$')

tidied_uirs = 'pickled/titdy_uris.pickle'
wsmall_statues = 'pickled/wsmall_statuses.pickle'
wsmall_statues_ar = 'pickled/wsmall_statuses_ar.pickle'
wsmall_statues_ar2 = 'pickled/wsmall_statuses2_ar.pickle'

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

ar_sites = ['britishnewspaperarchive.co.uk', 'webarchive.loc.gov',
            'webcitation.org',
            'webarchive.nationalarchives.gov.uk', 'archive.today']

arorg = 'archive.org'
warorg = 'web.archive.org'


def archives_map(it):
    for ars in ar_sites:
        if ars in it:
            return ars
    if arorg in it and warorg not in it:
        return arorg
    else:
        return warorg


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


def clean_new_wiki_name(name):
    m = match_end.findall(name)
    if len(m) > 0:
        return name.replace(m[0], '')
    else:
        return name.replace('.html', '')


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
    if os.path.exists(wsmall_latest_webarchive):
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
        return out
    else:
        return read_pickle('pickled/wsmallo_outl_temp.pickle')


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


def check_ar_outlinks(ars):
    if not os.path.exists(wsmall_statues_ar):
        result = {}
        temp = []
        processed = 0
        c = 0
        with FuturesSession(session=requests.Session(), executor=ProcessPoolExecutor(max_workers=10)) as session:
            for href in ars.href:
                temp.append(href)
                if len(temp) >= 100:
                    pending = []
                    for url in temp:
                        result[url] = -1
                        pending.append(session.head(url, headers={'User-Agent': useragents[c]}, timeout=5.0))
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
                        if processed % 100 == 0:
                            print(processed)
                    temp.clear()
        print('outise the with')
        had_status = {'archive': [], 'status': []}
        timed_out = {'archive': [], 'status': []}
        for k, v in result.items():
            ar = archives_map(k)
            if v == -1:
                timed_out['archive'].append(ar)
                timed_out['status'].append(v)
                continue
            had_status['archive'].append(ar)
            had_status['status'].append(v)
        hs = pd.DataFrame(had_status)
        to = pd.DataFrame(timed_out)
        dump_pickle((hs, to), wsmall_statues_ar)
        return hs, to
    else:
        return read_pickle(wsmall_statues_ar)


def check_wiki_live_web_links():
    if not os.path.exists(wsmall_latest_nwl_status):
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
                        pending.append(session.head(url, headers={'User-Agent': useragents[c]}, timeout=5.0))
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


def humansize(nbytes):
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    t = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (t, suffixes[i])


def get_sizes(sl, t):
    if os.path.exists(size_compare):
        out = defaultdict(dict)
        for f in sl:
            size = os.path.getsize(f)
            out[os.path.basename(f)]['oldf_sizeh'] = humansize(size)
            out[os.path.basename(f)]['oldf_size'] = size
            out[os.path.basename(f)]['newf_size'] = -1
            out[os.path.basename(f)]['newf_sizeh'] = -1
        for it in t:
            try:
                size = os.path.getsize(wsmall_latest_p % it['original'])
                out[it['original']]['newf_size'] = size
                out[it['original']]['newf_sizeh'] = humansize(size)
            except:
                continue
        with open(size_compare, 'w') as sout:
            sout.write('old_size,old_sizeh,new_size,new_sizeh,dif,idx\n')
            c = 0
            difm = 0
            for wfile, sizes in out.items():
                print(wfile, sizes)
                if sizes['newf_size'] == -1:
                    dif = -sizes['oldf_size']
                else:
                    dif = sizes['newf_size'] - sizes['oldf_size']
                difm += dif
                sout.write('%d,%s,%d,%s,%d,%d\n' % (
                    sizes['oldf_size'], sizes['oldf_sizeh'], sizes['newf_size'], sizes['newf_sizeh'], dif, c))
                c += 1


def statuses_to_csv():
    if os.path.exists(status_csv):
        with open(status_csv, 'w') as sout, open(status2_csv, 'w') as sout2:
            sout.write('link,domain,suffix,idx,status\n')
            sout2.write('link,domain,suffix,idx,status\n')
            statuses = read_pickle(wsmall_latest_nwl_status)
            c = 0
            for link, status in statuses.items():
                tld = tldextract.extract(link)
                if status == -1:
                    sout2.write('%s,%s,%s,%d,%s\n' % (link, tld.domain, tld.suffix, c, 'timedout'))
                elif status == -2:
                    sout2.write('%s,%s,%s,%d,%s\n' % (link, tld.domain, tld.suffix, c, 'ip'))
                else:
                    sout.write('%s,%s,%s,%d,%d\n' % (link, tld.domain, tld.suffix, c, status))
                c += 1
    statuses = read_pickle(wsmall_latest_nwl_status)
    with open('output_files/status_count.table', 'w') as out:
        c = Counter()
        for link, status in statuses.items():
            if status == -1:
                c['timedout'] += 1
            elif status == -2:
                c['ip'] += 1
            else:
                c[status] += 1
        headers = ['status', 'count']
        data = []

        for k, v in c.items():
            data.append([k, v])
        out.write(tabulate(data, headers=headers, tablefmt='latex'))


def combine_vocab():
    with open('output_files/wsmall-vocabn.csv', 'r') as wnv, open('output_files/wsmall-vocab.csv', 'r') as wov, \
            open('output_files/wsmall-vocab-combines.csv', 'w') as wvc:
        wvc.write('wc,vc,which\n')
        for row in csv.DictReader(wnv):
            wvc.write('%s,%s,%s\n' % (row['wc'], row['vc'], 'Live Web'))
        for row in csv.DictReader(wov):
            wvc.write('%s,%s,%s\n' % (row['wc'], row['vc'], 'Data Set'))


def compute_wnew_link_stats(ldf):
    if not os.path.exists('pickled/wsmall_nlinkstats.pickle'):
        only_wiki = pd.concat(
            [ldf[ldf.href.str.contains('/wiki')], ldf[ldf.href.str.contains('en.wikipedia.org/wiki')]])
        only_wiki.href = only_wiki.href.apply(lambda h: os.path.basename(h))
        only_wiki.wsmall_file = only_wiki.wsmall_file.apply(clean_new_wiki_name)
        wn_lstats = defaultdict(LinkDict)
        for owfile in only_wiki.wsmall_file.unique():
            owdf = only_wiki[only_wiki.wsmall_file == owfile]
            links_to = only_wiki[only_wiki.wsmall_file.isin(owdf.href)]
            links_to_other = owdf[~owdf.href.isin(links_to.href)]
            wn_lstats[owfile]['outlink_wsmall'] += links_to.wsmall_file.unique().size
            wn_lstats[owfile]['outlink_other'] += links_to_other.wsmall_file.unique().size
            wn_lstats[owfile]['total_outlinks'] += wn_lstats[owfile]['outlink_wsmall'] + wn_lstats[owfile][
                'outlink_other']
            for other in links_to.wsmall_file.unique():
                wn_lstats[other]['inlink'] += 1
        it = {'wsmall': [], 'outlink_wsmall': [], 'outlink_other': [], 'total_outlinks': [], 'inlinks': []}
        for name in wn_lstats.keys():
            it['wsmall'].append(name)
            it['outlink_wsmall'].append(wn_lstats[name]['outlink_wsmall'])
            it['outlink_other'].append(wn_lstats[name]['outlink_other'])
            it['total_outlinks'].append(wn_lstats[name]['total_outlinks'])
            it['inlinks'].append(wn_lstats[name]['inlink'])
        lstats_df = pd.DataFrame(it)
        dump_pickle(lstats_df, 'pickled/wsmall_nlinkstats.pickle')
        return lstats_df
    else:
        return read_pickle('pickled/wsmall_nlinkstats.pickle')
