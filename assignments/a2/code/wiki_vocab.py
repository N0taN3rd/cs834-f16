import re
import random
from string import punctuation
from util import wsmall2, read_pickle, dump_pickle
from bs4 import BeautifulSoup
from nltk.tokenize import TreebankWordTokenizer

no_wspace_punk = re.compile('(?:\s+)|[%s]' % re.escape(punctuation))


def vocab():
    w_list, w_set = read_pickle(wsmall2)
    toke = TreebankWordTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open('output_files/wsmal-vocab.txt', 'w+') as vout:
        for wf in w_list:
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    word_count += 1
                    if token not in vocab:
                        vocab.add(token)
                        vocab_count += 1
                        out = '%d %d\n' % (word_count, vocab_count)
                        print(out)
                        vout.write(out)


def vocab_backwards():
    w_list, w_set = read_pickle(wsmall2)
    toke = TreebankWordTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open('output_files/wsmal-vocabB.txt', 'w+') as vout:
        for wf in reversed(w_list):
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    word_count += 1
                    if token not in vocab:
                        vocab.add(token)
                        vocab_count += 1
                        out = '%d %d\n' % (word_count, vocab_count)
                        print(out)
                        vout.write(out)


def vocab_random():
    w_list, w_set = read_pickle(wsmall2)
    random.shuffle(w_list)
    toke = TreebankWordTokenizer()
    vocab = set()
    vocab_count = 0
    word_count = 0
    with open('output_files/wsmal-vocabR.txt', 'w+') as vout:
        for wf in w_list:
            with open(wf, 'r') as wIn:
                wSoup = BeautifulSoup(wIn.read(), 'lxml')
                for token in toke.tokenize(no_wspace_punk.sub(' ', wSoup.text)):
                    word_count += 1
                    if token not in vocab:
                        vocab.add(token)
                        vocab_count += 1
                        out = '%d %d\n' % (word_count, vocab_count)
                        print(out)
                        vout.write(out)


if __name__ == '__main__':
    vocab_random()