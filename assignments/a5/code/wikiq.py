from wiki_helpers import *
from wiki_vocab import *
from contextClasses import AutoSLatexTable


def web_ar(ldf):
    web_ars = check_webarchive(ldf)
    if not os.path.exists('output_files/webarchives.table'):
        if not os.path.exists('pickled/web_ard.pickle'):
            web_ar_counter = web_ars.copy(deep=True)
            web_ar_counter.href = web_ars.href.map(archives_map)
            dump_pickle(web_ar_counter, 'pickled/web_ard.pickle')
        else:
            web_ar_counter = read_pickle('pickled/web_ard.pickle')
        hrefc = ldf[ldf.href.str.contains(r'(www)|(http)')][~ldf.href.str.contains('wiki')].href.count()
        with AutoSLatexTable(list, 'output_files/webarchives.table',
                             ['Archive', 'Count', 'Percent Of Total Outlinks']) as arout:
            for it in web_ar_counter.groupby('href'):
                ar, df = it
                hc = df.href.count()
                arout.append([ar, hc, '{0}%'.format('%f' % ((hc / hrefc) * 100))])
                print(ar, hc, '{0}%'.format('%f' % ((hc / hrefc) * 100)))
    if not os.path.exists('output_files/webarchives_statuses.table'):
        had_status, timed_out = check_ar_outlinks(web_ars)
        with AutoSLatexTable(list, 'output_files/webarchives_statuses.table',
                             ['Archive', 'Status', 'Count', ]) as arout:
            for it in had_status.groupby(by=['archive', 'status']):
                ((ar, stat), df) = it
                c = df.status.count()
                arout.append([ar, stat, c])
                print(ar, stat, c)
        with AutoSLatexTable(list, 'output_files/webarchives_statuses_timeout.table',
                             ['Archive',  'Times Timed Out', ]) as arout:
            for it in had_status.groupby('archive'):
                ar, df = it
                c = df.status.count()
                arout.append([ar,c])
                print(ar, c)

if __name__ == '__main__':
    small_list, _ = read_pickle('pickled/wsmall.pickle')
    tidy = tidy_uris(small_list)
    w_statues = dl_pages(tidy)
    extract_links_count_vocab(wstatues=w_statues)
    link_df = get_link_df()
    extract_links_old(small_list)
    web_ar(link_df)
    old_ldf = get_oldl_df()
    wn_lstats = compute_wnew_link_stats(link_df)
    wo_lstats = old_wsmall_lstats_df()
    di = domain_info(link_df)
    check_wiki_live_web_links()
    statuses_to_csv()
    vocab_small()
    vocab_small_new()
