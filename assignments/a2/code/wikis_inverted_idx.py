import re
from collections import defaultdict
from util import wsmall2, wlarge2, read_pickle, dump_pickle
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer

no_wspace_punk = re.compile('(?:\s+)|[%s]|•' % re.escape("""!"#$%&()*+,./:;<=>?@[\]^_{|}~"""))


def small_inverted_idx_helper():
    w_list, w_set = read_pickle(wsmall2)
    toke = WordPunctTokenizer()
    with open('output_files/wsmall-word-file.txt', 'w+') as out:
        for wf in w_list:
            fname = wf[wf.rfind('/') + 1:]
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    if len(token) > 1:
                        lt = token.lower()
                        out.write('%s %s\n' % (lt, fname))


def build_inverted_idx_small():
    small_inverted_idx_helper()
    inverted_index = defaultdict(set)
    with open('output_files/wsmall-word-file.txt', 'r') as wIn:
        for line in wIn:
            sline = line.rstrip().split(' ')
            inverted_index[sline[0]].add(sline[1])
    dump_pickle(inverted_index, 'pickled/wsmall-inverted-index.pickle')
    with open('output_files/wsmall-inverted-index-count.txt', 'w') as iidx2Out:
        with open('output_files/wsmall-inverted-index.txt', 'w') as iidxOut:
            for k, v in sorted(inverted_index.items(), key=lambda idxE: len(idxE[1]), reverse=True):
                files = ' '.join(v)
                iidxOut.write('%s\t%s\n' % (k, files))
                iidx2Out.write('%s\t%d\n' % (k, len(v)))


def large_inverted_idx_helper():
    w_list, w_set = read_pickle(wlarge2)
    toke = WordPunctTokenizer()
    with open('output_files/wlarge-word-file.txt', 'w+') as out:
        for wf in w_list:
            fname = wf[wf.rfind('/') + 1:]
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    if len(token) > 1:
                        lt = token.lower()
                        out.write('%s %s\n' % (lt, fname))


def build_inverted_idx_large():
    large_inverted_idx_helper()
    inverted_index = defaultdict(set)
    with open('output_files/wlarge-word-file.txt', 'r') as wIn:
        for line in wIn:
            sline = line.rstrip().split(' ')
            inverted_index[sline[0]].add(sline[1])
    with open('output_files/large-inverted-index-count.txt', 'w') as iidx2Out:
        with open('output_files/large-inverted-index.txt', 'w') as iidxOut:
            for k, v in sorted(inverted_index.items(), key=lambda idxE: len(idxE[1]), reverse=True):
                files = ' '.join(v)
                iidxOut.write('%s\t%s\n' % (k, files))
                iidx2Out.write('%s\t%d\n' % (k, len(v)))


if __name__ == '__main__':
    build_inverted_idx_small()
    build_inverted_idx_large()
