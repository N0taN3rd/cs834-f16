import re
import os.path
import argparse
from nltk.corpus import brown, gutenberg, reuters, inaugural, words
from collections import Counter
from functional import pseq as parseq
from util import read_pickle, dump_pickle

only_words = re.compile('[a-z]+')


def build_word_count():
    if os.path.isfile('pickled/wcount.pickle'):
        return read_pickle('pickled/wcount.pickle')
    wcount = Counter()
    for fid in words.fileids():
        for word in words.words(fid):
            word = word.lower()
            if only_words.match(word) is not None:
                wcount[word] += 1
    for fid in gutenberg.fileids():
        for word in gutenberg.words(fid):
            word = word.lower()
            if only_words.match(word) is not None:
                wcount[word] += 1
    for fid in brown.fileids():
        for word in brown.words(fid):
            word = word.lower()
            if only_words.match(word) is not None:
                wcount[word] += 1
    for fid in reuters.fileids():
        for word in reuters.words(fid):
            word = word.lower()
            if only_words.match(word) is not None:
                wcount[word] += 1
    for fid in inaugural.fileids():
        for word in inaugural.words(fid):
            word = word.lower()
            if only_words.match(word) is not None:
                wcount[word] += 1
    dump_pickle(wcount, 'pickled/wcount.pickle')
    return wcount


def damerau_levenshtein(a, b):
    table = {}
    alphabet = {}
    for ac in a:
        alphabet[ac] = 0
    for bc in b:
        alphabet[bc] = 0
    lena = len(a)
    lenb = len(b)
    for i in range(lena + 1):
        table[i, 0] = i
    for j in range(lenb + 1):
        table[0, j] = j
    for i in range(1, lena + 1):
        db = 0
        for j in range(1, lenb + 1):
            k = alphabet[b[j - 1]]
            l = db
            cost = 0
            if a[i - 1] == b[j - 1]:
                db = j
            else:
                cost = 1
            table[i, j] = min(table[i - 1, j - 1] + cost,  # substitution
                              table[i, j - 1] + 1,  # insertion
                              table[i - 1, j] + 1)  # deletion
            if k > 0 and l > 0:
                table[i, j] = min(table[i, j], table[k - 1, l - 1] + (i - k - 1) + 1 + (j - l - 1))  # transposition
        alphabet[a[i - 1]] = i
    return table[lena, lenb]


def dist_away(mispell, wc, dist=2):
    return parseq(wc.keys()) \
        .map(lambda w: (w, damerau_levenshtein(mispell, w))) \
        .filter(lambda wdist: wdist[1] <= dist) \
        .map(lambda wdist: wdist[0]).to_set()


def probability(word, wc):
    return wc[word] / sum(wc.values())


def correct(mispell, wc):
    try:
        return max(dist_away(mispell, wc), key=lambda w: probability(w, wc))
    except Exception:
        return 'No Spellz Korrektion Found'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Korrect Yo Spellz')
    parser.add_argument('--wordz', type=str, nargs='+',
                        help='wordz to make spellz good',required=True)
    args = parser.parse_args()
    wc = build_word_count()
    for badd in args.wordz:
        print('The correction for the word',badd,'is')
        print(correct(badd, wc))
