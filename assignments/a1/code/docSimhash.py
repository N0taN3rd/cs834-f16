import os
import hashlib
import re
from math import floor
from fs.osfs import OSFS
from collections import Counter, defaultdict
from nltk import word_tokenize
from argparse import ArgumentParser
from string import punctuation
from random import uniform
from nltk.corpus import stopwords as noInclude
from scipy.spatial.distance import cosine
from itertools import combinations
from shared_code import *

noPunc = re.compile('[%s]' % re.escape(punctuation))
stopWords = set(noInclude.words('english'))
translate_table = dict((ord(char), ' ') for char in punctuation)


def doc_features_hash(text, bits):
    # sanitize the document by removing all punctuation
    clean = noPunc.sub(' ', text)
    # generate the token weights (frequency)
    c = Counter()
    for token in word_tokenize(clean):
        # exclude stopwords and single letter tokens
        if token not in stopWords and len(token) >= 2:
            c[token.lower()] += 1
    # generate the hashes by md5
    hashes = {}
    md5 = hashlib.md5()
    for token in c.keys():
        md5.update(token.encode('utf-8'))
        # http://stackoverflow.com/questions/26685067/represent-a-hash-string-to-binary-in-python
        the_hash = ''.join(format(ord(i), 'b') for i in md5.hexdigest())
        hashes[token] = the_hash[:bits]
    # return the token weights and hashes
    return c, hashes


def doc_features_hash_rand(text):
    """
    This version differs slightly
    Here we take the minimum hash value of all tokens
    as the length of the hash for all tokens
    The token length initially for all tokens
    is the length of the md5 hash transformed to a
    binary string
    """
    clean = noPunc.sub(' ', text)
    c = Counter()
    for token in word_tokenize(clean):
        if token not in stopWords and len(token) >= 2:
            c[token.lower()] += 1
    hashes = {}
    hash_lens = []
    md5 = hashlib.md5()
    for token in c.keys():
        md5.update(token.encode('utf-8'))
        the_hash = ''.join(format(ord(i), 'b') for i in md5.hexdigest())
        hashes[token] = the_hash
        hash_lens.append(len(the_hash))
    hash_len = min(hash_lens)
    return c, {token: hashes[token][:hash_len] for token in hashes.keys()}, hash_len


def gen_ith_of_v(i, hashes, weights):
    # generate the ith entry of vector V
    # accumulate values for the ith position in V
    toSum = []
    for token, the_hash in hashes.items():
        val = the_hash[i]
        weight = weights[token]
        if val == '1':
            toSum.append(1 * weight)
        else:
            toSum.append(-1 * weight)
    # sum the accumulated values resulting in the ith value of V
    return sum(toSum)


def file_fingerprint(file, rand_bits, bits):
    with open(file, 'r') as content_file:
        content = content_file.read()
    if rand_bits:
        feature_weights, feature_hashes, hash_len = doc_features_hash_rand(content)
        bits = hash_len
    else:
        feature_weights, feature_hashes = doc_features_hash(content, bits)
    fingerprint = []
    # generate the fingerprint
    for i in range(0, bits):
        # get the ith value of v
        ith_val = gen_ith_of_v(i, feature_hashes, feature_weights)
        # determine the ith value of the fingerprint
        if ith_val > 0:
            fingerprint.append(1)
        else:
            fingerprint.append(0)
    return fingerprint


def cosine_sim(hash1, hash2):
    # piggy back on scipy cosine distance
    # cosine similarity is 1 - cosine_distance
    return 1 - cosine(hash1, hash2)


def dir_sim_rand_helper(file_fps, combos):
    """
      As the simhashes between files of different types could
      potentially contain different lengths. This helper
      finds the minimum hash length for a common file extension.
      Then uses this length when checking for similarity
      between documents of same extension
    """
    common_ext = defaultdict(list)
    for f in file_fps.keys():
        ext = os.path.splitext(f)[1]
        common_ext[ext].append(len(file_fps[f]))
    real_len = {ext: min(common_ext[ext]) for ext in common_ext.keys()}
    for ext, bit_len in real_len.items():
        print('for ext %s the bit length is %d' % (ext, bit_len))
    print('----------------------------------------')
    for k, v in combos:
        kext = os.path.splitext(k)[1]
        vext = os.path.splitext(v)[1]
        if kext == vext:
            rlen = real_len[kext]
            print(k, v, cosine_sim(file_fps[k][:rlen], file_fps[v][:rlen]))


def dir_sim(dirp, randombits, bits):
    """
     Finds the similarity between documents of the same extension
     contained in the given directory path.
     If we are using random bits i.e md5 length the helper is used.
     For each file contained in the directory:
     get its fingerprint and generate the comparison combinations
     then for each combination who's extension matches
     print the similarity between them
    """
    if bits is not None:
        print('using bit len of %d' % bits)
    dir = OSFS(dirp)
    file_fps = {}
    for fname in dir.listdir(files_only=True):
        file_fps[fname] = file_fingerprint(os.path.join(dirp, fname), randombits, bits)
    dir.close()
    combos = list(map(dict, combinations(file_fps.items(), 2)))
    if bits is None:
        dir_sim_rand_helper(file_fps, combos)
        return
    for k, v in combos:
        kext = os.path.splitext(k)[1]
        vext = os.path.splitext(v)[1]
        if kext == vext:
            print(k, v, cosine_sim(file_fps[k][:bits], file_fps[v][:bits]))


if __name__ == '__main__':
    parser = ArgumentParser(description="Generate Simhash of a document", prog='docSimhash.py',
                            usage='%(prog)s [options]')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', '--file', help='file to use', action=FullPaths, type=is_file)
    mode.add_argument('-d', '--dir', help='directory to look for duplicates', action=FullPaths, type=is_dir)

    file_comp = mode.add_mutually_exclusive_group()
    file_comp.add_argument('-fc', '--filecomp', help='compare two files', action="store_true")
    file_comp.add_argument('-f1', '--file1', help='file one to use', action=FullPaths, type=is_file)
    file_comp.add_argument('-f2', '--file2', help='file two to use', action=FullPaths, type=is_file)

    bit_mode = parser.add_mutually_exclusive_group(required=True)
    bit_mode.add_argument('-b', '--bits', help='number of bits to use', type=int)
    bit_mode.add_argument('-md5b', '--md5bits', help='number of bits to use determined by md5 hash length',
                          action="store_true")
    bit_mode.add_argument('-randb', '--randombits', help='generate random bit length using value lowend highend', type=int, nargs='+')
    args = parser.parse_args()
    print()
    randy = False
    if args.randombits is not None:
        print("Generating random bit length using floor(random.uniform(low,high))")
        args.bits = floor(uniform(args.randombits[0], args.randombits[1]))

    if args.md5bits is True:
        print("Using bit length determined by the length of the md5 hash")
        randy = True

    if args.dir is not None:
        print('Comparing files contained in the directory %s' % args.dir)
        print('----------------------------------------')
        dir_sim(args.dir, randy, args.bits)
    else:
        if args.filecomp:
            file1_fp = file_fingerprint(args.file1, randy, args.bits)
            file2_fp = file_fingerprint(args.file2, randy, args.bits)
            print("The simhash similarity between %s and %s is %d" % (
            args.file1, args.file2, cosine_sim(file1_fp, file2_fp)))
        else:
            result = file_fingerprint(args.file, randy, args.bits)
            print("the simhash fingerprint for %s is %s" % (args.file, ''.join(str(fi) for fi in result)))
