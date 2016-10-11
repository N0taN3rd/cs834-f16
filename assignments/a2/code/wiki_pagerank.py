import re
import networkx as nx
from bs4 import BeautifulSoup
from urllib.parse import unquote
from util import *

local_wiki_re = re.compile('([.]{2}/){4}articles')

wiki_page_re = re.compile('(?:[.]{2}/){4}articles(?:/.){3}/(.+)')
wiki_http_page_re = re.compile('[a-z:/.]+(?:[.]{2}/){4}articles(?:/.){3}/(.+)')

nuke_tilda = re.compile('[A-Za-z]+~')


def no_image(a):
    return a.get('class') != ['image']


def get_edge_out(wfile, wfile_set):
    local_urls = []
    self_link = wfile[wfile.rfind('/') + 1:]
    with open(wfile, 'r') as wIn:
        wSoup = BeautifulSoup(wIn.read(), 'lxml')
        all_a = wSoup.find_all(href=local_wiki_re)
        for a in filter(no_image, all_a):
            furl = unquote(a['href'])
            rurl = nuke_tilda.sub('', furl[furl.rfind('/') + 1:])
            if rurl in wfile_set and rurl != self_link:
                local_urls.append((self_link, rurl))
    return self_link, local_urls


def get_edge_out2(wfile, nothing):
    local_urls = []
    self_link = wfile[wfile.rfind('/') + 1:]
    with open(wfile, 'r') as wIn:
        wSoup = BeautifulSoup(wIn.read(), 'lxml')
        all_a = wSoup.find_all(href=local_wiki_re)
        for a in filter(no_image, all_a):
            furl = unquote(a['href'])
            rurl = nuke_tilda.sub('', furl[furl.rfind('/') + 1:])
            if rurl != self_link:
                local_urls.append((self_link, rurl))
    return self_link, local_urls


def get_edge_out3(wfile, wfile_set):
    local_urls = []
    self_link = wfile[wfile.rfind('/') + 1:]
    with open(wfile, 'r') as wIn:
        wSoup = BeautifulSoup(wIn.read(), 'lxml')
        all_a = wSoup.find_all('a', href=True)
        for a in filter(no_image, all_a):
            href = unquote(a['href'])
            rurl = nuke_tilda.sub('', href[href.rfind('/') + 1:])
            if rurl in wfile_set and rurl != self_link:
                local_urls.append((self_link, rurl))
    return self_link, local_urls


def build_wlarge_edges():
    large_list, large_set = read_pickle(wlarge2)
    sl = []
    c = 0
    for wiki_file in large_list:
        c += 1
        self_link, out_links = get_edge_out(wiki_file, large_set)
        sl.append((self_link, out_links))
    dump_pickle(sl, wlarge_edges)


def wikil_soup():
    pair_soup = []
    c = 0
    large_list, large_set = read_pickle(wlarge2)
    for wiki_file in large_list:
        c += 1
        with open(wiki_file, 'r') as wIn:
            wSoup = BeautifulSoup(wIn.read(), 'lxml')
            pair_soup.append((wiki_file, str(wSoup)))
        if c % 1000 == 0:
            print(wiki_file)
    dump_pickle(pair_soup, 'pickled/wiki-large-soup.pickle')


def wiki_pagerank(w_list, w_set, edge_dump, graph_dump, edge_getter=get_edge_out):
    graph = nx.DiGraph()
    edge_list = []
    for wiki_file in w_list:
        self_link, out_links = edge_getter(wiki_file, w_set)
        graph.add_node(self_link)
        graph.add_edges_from(out_links)
        edge_list.append((self_link, out_links))
    dump_pickle(edge_list, edge_dump)
    w_pr = nx.pagerank_scipy(graph)
    dump_pickle((graph, w_pr), graph_dump)


def prout(wname):
    files = [('pickled/wiki-%s-graph.pickle' % wname, 'output_files/wiki-%s-pr20.csv' % wname),
             ('pickled/wiki-%s-graph2.pickle' % wname, 'output_files/wiki-%s-pr2-20.csv' % wname),
             ('pickled/wiki-%s-graph3.pickle' % wname, 'output_files/wiki-%s-pr3-20.csv' % wname)]
    for data, outfile in files:
        graph, pagerank = read_pickle(data)
        with open(outfile, 'w') as prOut:
            prOut.write('page,rank\n')
            for k, v in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
                prOut.write('%s,%.5f\n' % (k, v))


def wiki_small_pr():
    print('pr small')
    w_list, w_set = read_pickle(wsmall2)
    wiki_pagerank(w_list, w_set, wsmall_edges, wsmall_graph, get_edge_out)
    wiki_pagerank(w_list, w_set, wsmall_edges2, wsmall_graph2, get_edge_out2)
    wiki_pagerank(w_list, w_set, wsmall_edges3, wsmall_graph3, get_edge_out3)
    prout('small')


def wiki_large_pr():
    w_list, w_set = read_pickle(wlarge2)
    wiki_pagerank(w_list, w_set, wlarge_edges, wlarge_graph, get_edge_out)
    wiki_pagerank(w_list, w_set, wlarge_edges2, wlarge_graph2, get_edge_out2)
    wiki_pagerank(w_list, w_set, wlarge_edges3, wlarge_graph3, get_edge_out3)
    prout('large')


if __name__ == '__main__':
    edges = read_pickle(wlarge_edges)  # type: list[tuple[str, list[tuple[str,str]]]]
    with open('output_files/wlarge-nodEeges.csv','w+') as neOut:
        neOut.write('node,edge\n')
        for n,e in edges:
            if len(e) == 0:
                neOut.write('%s,\n'%n)
            else:
                for nn,ee in e:
                    neOut.write('%s,%s\n' % (nn,ee))
