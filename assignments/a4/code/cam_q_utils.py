import os
import re
from contextClasses import build_lstransformer

cacm_q_nums = [10, 20, 50, 100, 1000]


def sanitize_score(score):
    if score == 'NaN':
        return 0.0
    else:
        return score


def q_result_cleaner():
    camp = os.path.join(os.getcwd(), 'cacm/')
    return lambda fline: fline.rstrip().lstrip().replace(camp, '').replace('galago', '').replace('.html', '')


def q_results_sorter(file_obj):
    for line in sorted(file_obj, key=lambda fline: int(fline.split(' ')[0])):
        yield line


def is_good(rel, rel_ret):
    return not (rel is None or rel_ret['num_rel_ret'] == '0.00000' or rel_ret['num_rel_ret'] == 'NaN')


def rel_line_trans(key_where):
    def split_trans(flines):
        splitter = re.compile('\s+')
        transformer = build_lstransformer(lambda line: splitter.split(line)[key_where], seq_to='dict')
        return transformer(map(lambda x: x.rstrip().lstrip(), flines))

    return split_trans


def rel_docs_transform(num):
    def trans(gdict):
        results = gdict.get(num, None)
        if results is not None:
            rets = []
            for ret in results:
                qn, q0, doc, _ = ret.split(' ')
                rets.append(doc)
            return rets
        else:
            return None

    return trans


def rel_results_transform(num):
    def trans(gdict):
        splitter = re.compile('\s+')
        results = gdict.get(num, None)
        if results is not None:
            rets = {}
            for ret in results:
                method, doc, val = splitter.split(ret)
                rets[method] = val
            return rets
        else:
            return None

    return trans


def rel_all_results_transform(gdict):
    ret_list = []
    splitter = re.compile('\s+')
    for q, vals in gdict.items():
        ret = {}
        for val in vals:
            method, doc, score = splitter.split(val)
            ret[method] = score
        ret_list.append({'q': q, 'scores': ret})
    return ret_list
