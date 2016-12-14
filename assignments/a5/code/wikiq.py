from wiki_helpers import *

if __name__ == '__main__':
    # small_list, _ = read_pickle('pickled/wsmall.pickle')
    # tidy = tidy_uris(small_list)
    # w_statues = dl_pages(tidy)
    # extract_links_count_vocab(wstatues=w_statues)
    link_df = get_link_df()
    # extract_links_old(small_list)
    # check_webarchive(link_df)
    old_ldf = get_oldl_df()
    wn_lstats = compute_wnew_link_stats(link_df)
    wo_lstats = old_wsmall_lstats_df()

    print(wn_lstats)
    # di = domain_info(link_df)

    # check_wiki_live_web_links()
    # statuses_to_csv()
