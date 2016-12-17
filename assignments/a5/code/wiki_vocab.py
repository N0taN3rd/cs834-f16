import re
import random
import string
from util import wsmall, wsmalln, read_pickle, dump_pickle
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer

no_wspace_punk = re.compile('(?:\s+)|[%s]' % string.punctuation)


def vocab(wfile, outfile):
    w_list, w_set = read_pickle(wfile)
    toke = WordPunctTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open(outfile, 'w+') as vout:
        vout.write('wc,vc\n')
        for wf in w_list:
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    if len(token) > 1:
                        word_count += 1
                        if token not in vocab:
                            vocab.add(token)
                            vocab_count += 1
                            out = '%d,%d\n' % (word_count, vocab_count)
                            vout.write(out)


def vocab_backwards(wfile, outfile):
    w_list, w_set = read_pickle(wfile)
    toke = WordPunctTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open(outfile, 'w+') as vout:
        vout.write('wc,vc\n')
        for wf in reversed(w_list):
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    if len(token) > 1:
                        word_count += 1
                        if token not in vocab:
                            vocab.add(token)
                            vocab_count += 1
                            out = '%d,%d\n' % (word_count, vocab_count)
                            vout.write(out)


def vocab_random(wfile, outfile):
    w_list, w_set = read_pickle(wfile)
    random.shuffle(w_list)
    toke = WordPunctTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open(outfile, 'w+') as vout:
        vout.write('wc,vc\n')
        for wf in w_list:
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    if len(token) > 1:
                        word_count += 1
                        if token not in vocab:
                            vocab.add(token)
                            vocab_count += 1
                            out = '%d,%d\n' % (word_count, vocab_count)
                            vout.write(out)


def vocab_small():
    vocab(wsmall, 'output_files/wsmall-vocab.csv')
    vocab_backwards(wsmall, 'output_files/wsmall-vocabB.csv')
    vocab_random(wsmall, 'output_files/wsmall-vocabR.csv')


def vocab_small_new():
    vocab(wsmalln, 'output_files/wsmall-vocabn.csv')
    vocab_backwards(wsmalln, 'output_files/wsmall-vocabBn.csv')
    vocab_random(wsmalln, 'output_files/wsmall-vocabRn.csv')
