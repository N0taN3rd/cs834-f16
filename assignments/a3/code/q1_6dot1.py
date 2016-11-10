import json
import shlex
import statistics
from decimal import *
from subprocess import Popen, PIPE

import re
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from functional import pseq
from util import read_pickle, dump_pickle
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


class StemClazzIdx(dict):
    def __missing__(self, key):
        val = self[key] = StemClazz(key)
        return val


class StemClazz(object):
    def __init__(self, stem):
        self.stem = stem
        self.pair_scores = {}
        self.dice_score = None
        self.pairs = 0
        self.words = set()

    def add_pair_score(self, w1, w2, score):
        if self.pair_scores.get((w2, w1), None) is None:
            self.pair_scores[w1, w2] = float(score)
            self.pairs += 1
        self.words.add(w1)
        self.words.add(w2)

    def cumulative_dice(self):
        if self.dice_score is None:
            wc = len(self.words)
            if wc > 2:
                self.dice_score = sum(self.pair_scores.values()) / self.pairs
            else:
                self.dice_score = sum(self.pair_scores.values())
        return self.dice_score

    def clazz(self):
        return '/%s %.3f %s' % (self.stem, self.cumulative_dice(), ' '.join(sorted(self.words)))

    def __str__(self):
        return '%s %d %s' % (self.stem, len(self.words), self.pair_scores)

    def __repr__(self):
        return self.__str__()


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
        dump_pickle(stemmer_idx, 'pickled/stemmerIdx.pickle')
        for stemmer, stemdic in stemmer_idx.items():
            print('stemming index with %s' % stemmer)
            with open('output_files/idx_%s.txt' % stemmer, 'w') as stemOut:
                stemdic.write_class(stemOut)


def build_stem_queries():
    stemmer_idx = read_pickle('pickled/stemmerIdx.pickle')
    for stemmer, stemdic in stemmer_idx.items():
        print('building queries for %s' % stemmer)
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
        print('executing queries for %s' % stemmer)
        cline = './rungalago.sh threaded-batch-search %s' % qloc
        with open('output_files/%s_query_ret.trec' % stemmer, 'w') as retOut:
            runner = Popen(shlex.split(cline), stdout=retOut, stderr=PIPE)
            print(runner.stderr.read())


def write_dice():
    tol = Decimal(0.001)
    for stemmer in ['Lancaster', 'WordNetLemmatizer', 'PorterStemmer', 'SnowballStemmer']:
        count = {1: Counter(), 2: Counter()}
        print('calculating dice for %s' % stemmer)
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
                ab = a + b - counts
                dice = ab / (a + b)
                out.write('%s %.3f\n' % (stemC1C2, dice))
                if Decimal(dice) >= tol:
                    outf.write('%s %.3f\n' % (stemC1C2, dice))


def write_report():
    stemmer_idx = read_pickle('pickled/stemmerIdx3.pickle')
    look_for = 'admir'
    keep = []
    with open('output_files/q1_report.txt', 'w') as stemr:
        for stemmer in ['Lancaster', 'WordNetLemmatizer', 'PorterStemmer', 'SnowballStemmer']:
            print('writing report for %s' % stemmer)
            clazzIdx = StemClazzIdx()
            old_stemmer_idx = stemmer_idx[stemmer]
            with open('output_files/%s_dice_filtered.txt' % stemmer, 'r') as sin:
                for line in sin:
                    stemw1w2, score = line.rstrip().split(' ')
                    stem, w1, w2 = stemw1w2.split(',')
                    clazzIdx[stem].add_pair_score(w1, w2, score)
            oks = set(old_stemmer_idx.keys())
            nks = set(clazzIdx.keys())
            diff = oks.difference(nks)
            old_lens = []
            for old in diff:
                old_lens.append(len(old_stemmer_idx[old].stemsTo))
            with open('output_files/%s_new_stem_class.txt' % stemmer, 'w') as classOut:
                stemr.write('%s\n' % stemmer)
                stemr.write('The new stem classes had %d stems in common\n' % len(oks.intersection(nks)))
                stemr.write('%d stems not in the new stem classes\n' % len(diff))
                stemr.write('For the stems not in the new stem classes number of words\n')
                stemr.write('Mean: %d  Median: %d Mode: %d Max: %d\n' % (
                    statistics.mean(old_lens), statistics.median(old_lens), statistics.mode(old_lens), max(old_lens)))
                coverage = []
                for sclazz in sorted(clazzIdx.values(), key=lambda clazz: clazz.stem):
                    classOut.write('/%s,%.3f,%s\n' % (sclazz.stem, sclazz.cumulative_dice(), ' '.join(sclazz.words)))
                    if look_for == sclazz.stem:
                        keep.append((stemmer, sclazz))
                    coverage.append(sclazz.cumulative_dice())
                    old_stem = old_stemmer_idx[sclazz.stem]
                    oldwords = set(old_stem.stemsTo)
                    ondif = oldwords.difference(sclazz.words)
                    if len(ondif) > 0:
                        stemr.write('the original stem class %s had %d more words in it' % (sclazz.stem, len(ondif)))
                        stemr.write('the new stem class has a cumulative dice score of %d' % sclazz.cumulative_dice())
                stemr.write('For all stem classes cumulative Dice score\n')
                stemr.write('Mean: %.2f  Median: %.2f Mode: %.2f\n' % (
                    statistics.mean(coverage), statistics.median(coverage), statistics.mode(coverage)))
                stemr.write('----------------------------------------\n')
    print('writing final report section')
    with open('same.txt', 'w') as rout:
        for s, so in keep:
            rout.write('%s %s\n' % (s, so.clazz()))


if __name__ == '__main__':
    stem_index()
    build_stem_queries()
    write_dice()
    write_report()
