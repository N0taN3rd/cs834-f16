import re
import shlex
from collections import defaultdict
from subprocess import Popen, PIPE
from util import dump_pickle

isWord = re.compile('^[a-zA-Z]+$')


class Idx(dict):
    def __missing__(self, key):
        res = self[key] = Term(key)
        return res


class Term(object):
    def __init__(self, term):
        self.term = term
        self.docwhere = defaultdict(list)

    def add_doc_where(self, doc, where):
        self.docwhere[doc].extend(where)

    def is_word(self):
        return isWord.match(self.term) is not None

    def __str__(self):
        return '%s %s' % (self.term, self.docwhere)

    def __repr__(self):
        return self.__str__()


def galago_postingd_csv():
    cline = './rungalago.sh dump-index index'
    with open('output_files/idx3.csv', 'w') as retOut:
        runner = Popen(shlex.split(cline), stdout=retOut, stderr=PIPE)
        print(runner.stderr.read())
    idx = Idx()
    with open('idx3.csv', 'r') as gal:
        for line in gal:
            lsplit = line.rstrip().lstrip().split(',')
            word = lsplit[0]
            doc = lsplit[1]
            at = lsplit[2:]
            idx[word].add_doc_where(doc, at)
    dump_pickle(idx,'pickled/idx3.pickle')
    with open('output_files/idx3_terms.txt','w') as termOut:
        termOut.write(' '.join(sorted(filter(lambda x: isWord.match(x) is not None,list(idx.keys())))))


if __name__ == '__main__':
    galago_postingd_csv()
