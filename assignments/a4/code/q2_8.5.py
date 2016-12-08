from assignmentFilePaths import *
from cam_q_utils import *
from contextClasses import SelectFromFile, AutoSaveCsv


def select_rel_results_save(relp, csvp):
    with SelectFromFile(relp, selector=rel_all_results_transform, transformer=rel_line_trans(1)) as rel_ret, \
            AutoSaveCsv(list, csvp, ['q', 'MAP', 'R-Prec', 'NDCG5', 'NDCG10', 'P10']) as out:
        for qret in rel_ret:
            out.append({
                'q': qret['q'],
                'MAP': sanitize_score(qret['scores']['map']),
                'R-Prec': sanitize_score(qret['scores']['R-prec']),
                'NDCG5': sanitize_score(qret['scores']['ndcg5']),
                'NDCG10': sanitize_score(qret['scores']['ndcg10']),
                'P10': sanitize_score(qret['scores']['P10'])
            })
            out.sort(key=lambda q: int(q['q']))


def count_relevant_docs():
    transformer1 = rel_line_trans(0)
    with SelectFromFile(cacm_rel, selector=lambda x: x, transformer=transformer1) as rel, \
            AutoSaveCsv(list, 'output_files/reldocs_count.csv', ['q', 'count']) as out:
        for doc, rels in sorted(rel.items(), key=lambda x: int(x[0])):
            print(doc, len(rels))
            out.append({
                'q': doc,
                'count': len(rels)
            })
            out.sort(key=lambda q: int(q['q']))


if __name__ == '__main__':
    print('generating the csv file for 10 requested documents for all cacm queries')
    select_rel_results_save(cacm_rel_out, cacm_all_rel_csv_reqnum % 10)
    count_relevant_docs()

