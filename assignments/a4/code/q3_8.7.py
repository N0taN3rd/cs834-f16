from assignmentFilePaths import *
from cam_q_utils import *
from contextClasses import SelectFromFile, AutoSaveCsv


def select_rel_results_save(relp, csvp):
    with SelectFromFile(relp, selector=rel_all_results_transform, transformer=rel_line_trans(1)) as rel_ret:
        keys = list(rel_ret[0]['scores'].keys())
        fields = ['q']
        fields.extend(keys)
        with AutoSaveCsv(list, csvp, fields) as out:
            for qret in rel_ret:
                qstats = { 'q': qret['q'] }
                for k in keys:
                    qstats[k] = sanitize_score(qret['scores'][k])
                out.append(qstats)
                out.sort(key=lambda q: int(q['q']))


if __name__ == '__main__':
    for requested in cacm_q_nums:
        print(
            'generating the csv file for R-precision comparison for %d requested documents for all cacm queries' %
            requested)
        csvp = cacm_all_rel_csv_rp_compare % requested
        if requested != 10:
            relp = cacm_rel_rnum_out % requested
        else:
            relp = cacm_rel_out
        select_rel_results_save(relp, csvp)
