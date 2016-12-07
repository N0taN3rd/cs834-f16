import json
import os
import math
from subprocess import Popen, PIPE
from shlex import split
from itertools import islice
from assignmentFilePaths import cacm_qs, cacm_q_xml
from contextClasses import BeautifulSoupFromFile


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def join_with_cwd(name):
    return os.path.join(os.getcwd(), name)


def file_name(file_p):
    return os.path.basename(file_p)


def select_n(ilist, n=10):
    return list(islice(ilist, n))


def path_exists(path):
    return os.path.exists(path)


def run_galago(cline, stdout=PIPE, stderror=PIPE):
    return Popen(split(cline), stdout=stdout, stderr=stderror)


def rand_select_stripper(ilist):
    return map(lambda s: s.lstrip().rstrip(), ilist)


def forward_galago_output(cline, outp):
    return run_galago(cline, stdout=outp)


def galago_mk_index(idxp, inp):
    if not path_exists(idxp):
        cline = './rungalago.sh build %s %s' % (idxp, inp)
        return run_galago(cline=cline)
    else:
        return None


def galago_search(qpath, idxpath, requested=10, retpath=None):
    cline = './rungalago.sh threaded-batch-search --requested=%d --index=%s %s' % (requested, idxpath, qpath)
    if retpath is not None:
        with open(retpath, 'w') as retOut:
            runner = run_galago(cline=cline, stdout=retOut)
            stdout, stderr = runner.communicate()
            print(stderr)
            return runner.returncode
    else:
        return run_galago(cline=cline)


def cam_xmlqs_to_json(idxp):
    with BeautifulSoupFromFile(cacm_q_xml, mode='xml') as soup:
        orginal_queries = soup.find_all('query')
        updated_queries = []
        with open(cacm_qs, 'w') as camqjson:
            for xmlq in orginal_queries:
                updated_queries.append({
                    'number': xmlq.number.text.strip(),
                    'text': xmlq.find('text').text.lstrip().rstrip()
                })
            json.dump({
                'queries': updated_queries,
                'index': idxp,
                'queryType': 'simple'
            }, camqjson, indent=2)
