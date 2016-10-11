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

def small():
    graph, pagerank = read_pickle(wsmall_graph)  # type: tuple[nx.DiGraph, dict]
    inlinks = []
    for n in graph.nodes():
        ins = graph.in_edges(n)
        if len(ins) > 0:
            inlinks.append((n, len(ins)))
    w_list, w_set = read_pickle(wsmall2)
    with open('output_files/wiki-small-inlinksc.csv','w+') as loc:
        with open('output_files/wiki-small-inlinks.csv','w+') as loc2:
            loc.write('page,count\n')
            loc2.write('page,atext\n')
            for n, c in sorted(inlinks, key=lambda x: x[1], reverse=True)[:10]:
                for fp in w_list:
                    wp = fp[fp.rfind('/') + 1:]
                    if n == wp:
                        print(fp, n, c)
                        loc.write('%s,%d\n'%(n,c))
                        at = []
                        with open(fp, 'r') as wIn:
                            wSoup = BeautifulSoup(wIn.read(), 'lxml')
                            all_a = wSoup.find_all(href=local_wiki_re)
                            for a in filter(no_image, all_a):
                                if a.string is not None:
                                    at.append(a.string)
                        loc2.write('%s,%s\n'%(n,':'.join(at)))



def large():
    graph, pagerank = read_pickle(wlarge_graph)  # type: tuple[nx.DiGraph, dict]
    inlinks = []
    for n in graph.nodes():
        ins = graph.in_edges(n)
        if len(ins) > 0:
            inlinks.append((n, len(ins)))
    w_list, w_set = read_pickle(wlarge2)
    with open('output_files/wiki-large-inlinksc.csv', 'w+') as loc:
        with open('output_files/wiki-large-inlinks.csv', 'w+') as loc2:
            loc.write('page,count\n')
            loc2.write('page,atext\n')
            for n, c in sorted(inlinks, key=lambda x: x[1], reverse=True)[:10]:
                for fp in w_list:
                    wp = fp[fp.rfind('/') + 1:]
                    if n == wp:
                        print(fp, n, c)
                        loc.write('%s,%d\n' % (n, c))
                        at = []
                        with open(fp, 'r') as wIn:
                            wSoup = BeautifulSoup(wIn.read(), 'lxml')
                            all_a = wSoup.find_all(href=local_wiki_re)
                            for a in filter(no_image, all_a):
                                if a.string is not None:
                                    at.append(a.string)
                        loc2.write('%s,%s\n' % (n, ':'.join(at)))


if __name__ == '__main__':
    small()
    print('----------------------------------------')
    large()
