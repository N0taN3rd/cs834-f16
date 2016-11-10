import shlex
import re
import math
from subprocess import Popen, PIPE
from util import dump_pickle, read_pickle
from collections import Counter

only_words = re.compile('^[a-zA-Z]+~[a-zA-Z]+$')


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
                self.coverage = '%.2f' % round(bothp, 1) + '% fully covered' + ' %.2f' % round(ostemp,
                                                                                               1) + '% matches stem'
            elif self.ostem == 0:
                self.coverage = '100% fully covered'
            else:
                self.coverage = '100% only matches stem'

    def __str__(self):
        return '%s %d %s %s' % (self.clazz, self.matchesOld, self.coverage, self.matchesStem,)

    def __repr__(self):
        return self.__str__()


def dice(a, b, ab_wins, ab_count):
    return (2 * ab_wins[a, b]) / (ab_count[a] + ab_count[b])


def mi(a, b, ab_wins, ab_count, nwin):
    return ab_wins[a, b] / (ab_count[a] * ab_count[b])


def emi(a, b, ab_wins, ab_count, nwin):
    return (ab_wins[a, b] / nwin) * math.log(nwin * (ab_wins[a, b] / (ab_count[a] * ab_count[b])))


def chi(a, b, ab_wins, ab_count, nwin):
    top = (ab_wins[a, b] - ((1 / nwin) * ab_count[a] / nwin * ab_count[b] / nwin))
    return (math.pow(top, 2)) / ((ab_count[a] / nwin) * (ab_count[b] / nwin))


class Win5Ret(object):
    def __init__(self, a, b, ab_wins, ab_count, nwin):
        self.a = a
        self.b = b
        self.dice = dice(a, b, ab_wins, ab_count)
        self.mi = mi(a, b, ab_wins, ab_count, nwin)
        self.emi = emi(a, b, ab_wins, ab_count, nwin)
        self.chi = chi(a, b, ab_wins, ab_count, nwin)

    def __str__(self):
        return '%s, %s dice: %.5f mi: %.5f emi: %.5f chi %.5f' % (
            self.a, self.b, self.dice, self.mi, self.emi, self.chi)

    def __repr__(self):
        return self.__str__()

    def write_csv(self, out):
        out.write('%s, %s, %.5f, %.5f, %.10f,%.5f\n' % (
            self.a, self.b, self.dice, self.mi, self.emi, self.chi))


def dump_window_idx():
    cline = './rungalago.sh dump-index windowIdx/od.n2.w5.h2'
    with open('output_files/window5/ordered5idx.txt', 'w') as retOut:
        runner = Popen(shlex.split(cline), stdout=retOut, stderr=PIPE)
        print(runner.stderr.read())
    ab_count = Counter()
    ab_count_wins = Counter()
    wins = 0
    with open('output_files/window5/ordered5idx.txt', 'r') as oin:
        for line in oin:
            splitted = line.rstrip().split(',')
            if only_words.match(splitted[0]) is not None:
                a, b = splitted[0].split('~')
                ab_count[a] += 1
                ab_count[b] += 1
                wins += 1
                ab_count_wins[a, b] += 1

    dump_pickle((ab_count, ab_count_wins, wins), 'pickled/window5Counts.pickle')


def association_measures():
    dump_window_idx()
    ab_count, ab_count_wins, wins = read_pickle('pickled/window5Counts.pickle')
    rets = []
    for (a, b) in ab_count_wins.keys():
        rets.append(Win5Ret(a, b, ab_count_wins, ab_count, wins))
    with open('output_files/window5/ordered5associationret.csv', 'w') as out:
        for ret in sorted(rets, key=lambda w5r: w5r.dice, reverse=True):
            ret.write_csv(out)


if __name__ == '__main__':
    dump_window_idx()
    association_measures()
