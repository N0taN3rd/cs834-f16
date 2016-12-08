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


if __name__ == '__main__':
    for requested in cacm_q_nums:
        print('generating the csv file for %d requested documents for all cacm queries' % requested)
        csvp = cacm_all_rel_csv_reqnum % requested
        if requested != 10:
            relp = cacm_rel_rnum_out % requested
        else:
            relp = cacm_rel_out
        select_rel_results_save(relp, csvp)