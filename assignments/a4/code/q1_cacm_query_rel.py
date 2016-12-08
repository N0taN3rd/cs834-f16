from util import *
from contextClasses import *
from assignmentFilePaths import *
from cam_q_utils import *
from ranking_methods import ndcg_at_k, average_precision, precision_at_k


def build_idx_qs():
    idx_maker = galago_mk_index(cacm_idx, cacm_in)
    if idx_maker is not None:
        print('making cacm index')
        stdout, stderr = idx_maker.communicate()
        rc = idx_maker.returncode
        if rc != 0:
            print('we had failure making the index for cacm')
        else:
            print('converting xml queries to json')
            cam_xmlqs_to_json(cacm_idx)
    else:
        print('the index was already created')


def execute_queries(qresult_path=cacm_q_out_p, rel_outp=cacm_rel_out, num=10):
    if not path_exists(qresult_path):
        print('executing cacm queries', num)
        rc = galago_search(qpath=cacm_qs, idxpath=cacm_idx, retpath=qresult_path, requested=num)
        if rc != 0:
            print(
                'we might have had error while executing queries\nif the ouput does not display '
                'org.lemurproject.galago.core.tools.apps.ThreadedBatchSearch run\nINFO: Still running... \nthere was '
                'an issue')
        import time
        print('executed the queries using threaded batch waiting 5 seconds for galago to finish')
        time.sleep(5)
        print('finished executing queries sanitizing output')
        with CleanFileLines(qresult_path, q_result_cleaner(), sort_output=q_results_sorter, save_back=True):
            print('finished sanitizing output')
    else:
        print('cam queries were already executed')

    if not path_exists(rel_outp):
        print('retrieving the evaluation for the queries and the relevance judgments')
        cline = './rungalago.sh eval cacm/cacm.rel %s %d' % (qresult_path, num)
        with RunCommandSaveOut(cline, rel_outp, command_fun=forward_galago_output, print_file=True) as g_eval:
            rc = g_eval.returncode
            print('finished retrieving the evaluation for the queries and the relevance judgments')
    else:
        print('the evaluation for the queries and the relevance judgments has already been generated')


def run_queries():
    qresult_path = cacm_q_out_p
    rel_outp = cacm_rel_out
    execute_queries(qresult_path=qresult_path, rel_outp=rel_outp, num=10)


def eval_q_relevancej():
    transformer = ltransformer_group_by(lambda line: line.split(' ')[0])
    with RandFinderFile(cacm_q_out_p, transformer=transformer) as (num, qs):
        print('randomly selected query %s from the cam queries' % num)
        query_results_pos = {}
        doc_list = []
        print('the results for query %s are' % num)
        for qline in rand_select_stripper(qs):
            qn, q0, doc, pos, score = qline.split(' ')
            doc_list.append(doc)
            print('%s @pos=%s' % (doc, pos))
            query_results_pos[doc] = pos, score
        transformer1 = rel_line_trans(0)
        transformer2 = rel_line_trans(1)
        with SelectFromFile(cacm_rel, selector=rel_docs_transform(num), transformer=transformer1) as rel, \
                SelectFromFile(cacm_rel_out, selector=rel_results_transform(num), transformer=transformer2) as rel_ret:

            if not is_good(rel, rel_ret):
                print('no relevant documents for query %s' % num)
            else:
                print('\nquery %s has %d relevant documents' % (num, len(rel)))
                reciprocal_rank = None
                reciprocal_ranks = None
                rr_found = False
                count = 1
                for doc in rel:
                    it = query_results_pos.get(doc, None)
                    if it is not None:
                        print('the %s relevant document %s was found in the result set at @pos=%s' % (
                            ordinal(count), doc, it[0]))
                        if not rr_found:
                            reciprocal_rank = '%.2f' % (1 / int(it[0]))
                            reciprocal_ranks = '1/%s' % it[0]
                            rr_found = True
                        count += 1
                calc_list = []
                for ret_doc in doc_list:
                    if ret_doc in rel:
                        calc_list.append(1)
                    else:
                        calc_list.append(0)

                print('\nthe relevance results for the query %s are' % num)
                print('the binary representation of the runs returned documents is', calc_list)
                print('Average Precision = %.2f' % average_precision(calc_list))
                print('NDCG at 5 = %.2f' % ndcg_at_k(calc_list, 5))
                print('NDCG at 10 = %.2f' % ndcg_at_k(calc_list, 10))
                print('Precision at 10 = %.2f' % precision_at_k(calc_list, 10))
                print('Reciprocal Rank %s =' % reciprocal_ranks, reciprocal_rank)
                print('Galago NDCG at 5:', rel_ret['ndcg5'])
                print('Galago NDCG at 10:', rel_ret['ndcg10'])
                print('Galago Precision at 10:', rel_ret['P10'])


if __name__ == '__main__':
    build_idx_qs()
    run_queries()
    eval_q_relevancej()
