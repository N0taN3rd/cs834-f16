import json
import shlex
from collections import defaultdict

import networkx as nx
from networkx.drawing.nx_agraph import write_dot, to_agraph
from networkx import Graph, DiGraph
from decimal import *
from subprocess import Popen, PIPE
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from functional import seq, pseq
from util import dump_pickle, read_pickle
from itertools import combinations
from collections import Counter

portStemmer = PorterStemmer()
snowBall = SnowballStemmer('english')
wordNet = WordNetLemmatizer()
lancaster = LancasterStemmer()


class StemmerIdx(dict):
    def __missing__(self, key):
        ret = self[key] = StemIdx()
        return ret


class StemIdx(dict):
    def __missing__(self, key):
        ret = self[key] = Stem(key)
        return ret

    def write_class(self, out):
        for stem in sorted(self.values(), key=lambda stem: stem.stem):
            stem.write_stem(out)


class Stem(object):
    def __init__(self, stem):
        self.stem = stem
        self.stemsTo = []

    def add_term(self, term):
        self.stemsTo.append(term)

    def write_stem(self, out):
        out.write('/%s %s\n' % (self.stem, ' '.join(self.stemsTo)))

    def __str__(self):
        return '%s %s' % (self.stem, self.stemsTo)

    def __repr__(self):
        return self.__str__()


class StemClazz(object):
    def __init__(self, line):
        self.clazz = line.split(' ')
        self.matchesOld = 0
        self.matchesStem = []
        self.coverage = ''
        self.cboth = 0
        self.ostem = 0

    def search(self, alphaList):
        for alphaStem in alphaList:
            if alphaStem.stem in self.clazz:
                self.matchesOld += 1
                matchCount = 0
                for term in alphaStem.stemsTo:
                    if term in self.clazz:
                        matchCount += 1
                if matchCount == len(alphaStem.stemsTo):
                    self.matchesStem.append((alphaStem.stem, 'contains stem & terms'))
                else:
                    self.matchesStem.append((alphaStem.stem, 'matches only stem'))

    def cal_coverage(self):
        for stem, howMuch in self.matchesStem:
            if howMuch == 'contains stem & terms':
                self.cboth += 1
            else:
                self.ostem += 1
        if self.matchesOld == 1:
            if self.cboth > 0:
                self.coverage = '100% fully covered'
            else:
                self.coverage = '100% only matches stem'
        else:
            if self.cboth > 0 and self.ostem > 0:
                bothp = self.cboth / self.matchesOld
                ostemp = self.ostem / self.matchesOld
                self.coverage = '%.2f' % round(bothp,1) + '% fully covered' + ' %.2f' % round(ostemp,1) + '% matches stem'
            elif self.ostem == 0:
                self.coverage = '100% fully covered'
            else:
                self.coverage = '100% only matches stem'

    def __str__(self):
        return '%s %d %s %s' % (self.clazz, self.matchesOld, self.coverage, self.matchesStem,)

    def __repr__(self):
        return self.__str__()


class CountDict(dict):
    def __missing__(self, key):
        ret = self[key] = CoverageDict()
        return ret


class CoverageDict(dict):
    def __missing__(self, key):
        ret = self[key] = Counter()
        return ret


def stem_map(x):
    ps = portStemmer.stem(x)
    nb = snowBall.stem(x)
    wn = wordNet.lemmatize(x)
    lan = lancaster.stem(x)
    return [('PorterStemmer', ps, x), ('SnowballStemmer', nb, x), ('WordNetLemmatizer', wn, x), ('Lancaster', lan, x)]


def fold_fun(accum, val):
    stemmer, stem, term = val
    accum[stemmer][stem].add_term(term)
    return accum


def stem_index():
    with open('output_files/idx3_terms.txt', 'r') as alpha:
        words = alpha.readline()
        stemmer_idx = pseq(words.split(' ')) \
            .flat_map(stem_map) \
            .fold_left(StemmerIdx(), fold_fun)
        dump_pickle(stemmer_idx, 'pickled/stemmerIdx3.pickle')
        for stemmer, stemdic in stemmer_idx.items():
            print(stemmer)
            with open('output_files/idx3_%s.txt' % stemmer, 'w') as stemOut:
                stemdic.write_class(stemOut)


# pip3 freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip3 install -U

def build_stem_queries():
    stemmer_idx = read_pickle('pickled/stemmerIdx3.pickle')
    for stemmer, stemdic in stemmer_idx.items():
        queries = []
        c = 0
        for stem in stemdic.values():
            if len(stem.stemsTo) > 1:
                c += 3
                for c1, c2 in combinations(stem.stemsTo, 2):
                    if c1 is None or c2 is None:
                        raise Exception('bad field')
                    queries.append({
                        'number': '%s,%s' % (stem.stem, c1),
                        'text': '#combine( #dirichlet( #extents:@/%s/:part=postings() ) )' % c1
                    })
                    queries.append({
                        'number': '%s,%s' % (stem.stem, c2),
                        'text': '#combine( #dirichlet( #extents:@/%s/:part=postings() ) )' % c2
                    })
                    queries.append({
                        'number': '%s,%s,%s' % (stem.stem, c1, c2),
                        'text': '#combine( #dirichlet( #extents:@/%s/:part=postings() ) #dirichlet('
                                '#extents:@/%s/:part=postings() ) )' % (c1, c2)
                    })
            else:
                c += 1
                queries.append({
                    'number': '%s,%s' % (stem.stem, stem.stemsTo[0]),
                    'text': '#combine( #dirichlet( #extents:@/%s/:part=postings() ) )' % stem.stemsTo[0]
                })
        qloc = 'galagoqueries/%s.json' % stemmer
        with open(qloc, 'w') as qout:
            json.dump({
                'queries': queries,
                'index': 'index3',
                'queryType': 'complex'
            }, qout, indent=2)
        #
        cline = './rungalago.sh threaded-batch-search %s' % qloc
        print(shlex.split(cline))
        with open('output_files/%s_query_ret.trec' % stemmer, 'w') as retOut:
            runner = Popen(shlex.split(cline), stdout=retOut, stderr=PIPE)
        print(runner.stderr.read())
        print(runner.returncode)


def write_dice():
    # build_stem_queries()
    tol = Decimal(0.001)
    for stemmer in ['Lancaster', 'WordNetLemmatizer', 'PorterStemmer', 'SnowballStemmer']:
        count = {1: Counter(), 2: Counter()}
        print(stemmer)
        with open('output_files/%s_query_ret.trec' % stemmer, 'r') as trec, \
                open('output_files/%s_dice.txt' % stemmer, 'w') as out, \
                open('output_files/%s_dice_filtered.txt' % stemmer, 'w') as outf:
            for line in trec:
                it = line.rstrip().split(' ')[0]
                count[it.count(',')][it] += 1
            for stemC1C2, counts in sorted(count[2].items(), key=lambda x: x[0]):
                stem, c1, c2 = stemC1C2.split(',')
                a = count[1]['%s,%s' % (stem, c1)]
                b = count[1]['%s,%s' % (stem, c2)]
                # cause combine is or https://sourceforge.net/p/lemur/wiki/Belief%20Operations/
                ab = (a + b) - counts
                dice = ab / (a + b)
                out.write('%s %.3f\n' % (stemC1C2, dice))
                if Decimal(dice) >= tol:
                    outf.write('%s %.3f\n' % (stemC1C2, dice))


def find_connected():
    print('hi')
    for stemmer in ['Lancaster', 'WordNetLemmatizer', 'PorterStemmer', 'SnowballStemmer']:
        with open('output_files/%s_dice_filtered.txt' % stemmer, 'r') as sin, \
                open('output_files/%s_dice_connected.txt' % stemmer, 'w') as out, \
                open('output_files/%s_dice_sconnected.txt' % stemmer, 'w') as out2:
            g = DiGraph()
            g2 = Graph()
            nodes = set()
            edges = set()
            for line in sin:
                stemC1C2, dice = line.rstrip().split(' ')
                stem, c1, c2 = stemC1C2.split(',')
                nodes.add(stem)
                nodes.add(c1)
                nodes.add(c2)
                edges.add((stem, c1, float(dice)))
                edges.add((stem, c2, float(dice)))
                edges.add((c1, stem, float(dice)))
                edges.add((c2, stem, float(dice)))
            for n in nodes:
                g.add_node(n)
                g2.add_node(n)
            for stem, term, dice in edges:
                g.add_edge(stem, term, weight=dice)
                g2.add_edge(stem, term, weight=dice)
            for connected in nx.connected_components(g):
                out.write('%s\n' % ' '.join(connected))
            for connected in nx.strongly_connected_components(g):
                out2.write('%s\n' % ' '.join(connected))


def coverageReport():
    stemmer_idx = read_pickle('pickled/stemmerIdx3.pickle')
    for stemmer in ['Lancaster', 'WordNetLemmatizer', 'PorterStemmer', 'SnowballStemmer']:
        with open('output_files/%s_dice_connected.txt' % stemmer, 'r') as sin, \
                open('output_files/%s_dice_sconnected.txt' % stemmer, 'r') as sin2:
            stemdic = stemmer_idx[stemmer]
            writeCoverage(stemmer, stemdic, 'connected', sin)
            writeCoverage(stemmer, stemdic, 'sconnected', sin2)


def writeCoverage(stemmer, stemdic, clust, sin):
    alphaStem = defaultdict(list)
    for stem in stemdic.values():
        alphaStem[stem.stem[0]].append(stem)
    alphaStemClazz = defaultdict(list)
    for line in sin:
        line = line.rstrip()
        alphaStemClazz[line[0]].append(StemClazz(line))
    for alpha, stemclzzs in alphaStemClazz.items():
        for sclzz in stemclzzs:
            sclzz.search(alphaStem[alpha])
    alphaClazzCover = defaultdict(CoverageDict)
    for alpha, stemclzzs in alphaStemClazz.items():
        for sclzz in stemclzzs:
            sclzz.cal_coverage()
            alphaClazzCover[len(sclzz.clazz)][sclzz.matchesOld][sclzz.coverage] += 1
    with open('output_files/%s_stemclass_%s.csv' % (stemmer, clust), 'w') as covOut:
        covOut.write('sizeClass,matches,covers,count\n')
        for sizeClazz, mathnum in sorted(alphaClazzCover.items(), key=lambda x: x[0], reverse=True):
            for matches, coverages in sorted(mathnum.items(), key=lambda x: x[0], reverse=True):
                for covers, count in sorted(coverages.items(), key=lambda x: x[1], reverse=True):
                    print(sizeClazz, matches, covers, count)
                    covOut.write('%d,%d,%s,%d\n' % (sizeClazz, matches, covers, count))
                print('----------------------------------------')
            print('+++++++++++++++++++++++++++++++++++++++++')


if __name__ == '__main__':
    # write_dice()
    # find_connected()
    coverageReport()
