import re
from collections import defaultdict
from string import punctuation
from util import wsmall2, read_pickle, dump_pickle
from bs4 import BeautifulSoup
from nltk.tokenize import TreebankWordTokenizer

no_wspace_punk = re.compile('(?:\s+)|[%s]|•' % re.escape(punctuation))


def build_inverted_idx_small():
    inverted_index = defaultdict(set)
    w_list, w_set = read_pickle(wsmall2)
    toke = TreebankWordTokenizer()
    for wf in w_list:
        fname = wf[wf.rfind('/') + 1:]
        with open(wf, 'r') as wIn:
            wSoup = BeautifulSoup(wIn.read(), 'html5lib')
            for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                lt = token.lower()
                inverted_index[lt].add(fname)
    dump_pickle(inverted_index, 'pickled/wsmall-inverted-index.pickle')
    with open('output_files/wsmall-inverted-index-count.txt', 'w') as iidx2Out:
        with open('output_files/wsmall-inverted-index.txt', 'w') as iidxOut:
            for k, v in sorted(inverted_index.items(), key=lambda idxE: len(idxE[1]), reverse=True):
                files = ' '.join(v)
                iidxOut.write('%s\t%s\n' % (k, files))
                iidx2Out.write('%s\t%d\n' % (k, len(v)))


if __name__ == '__main__':
    build_inverted_idx_small()

