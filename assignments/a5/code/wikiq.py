import csv

from wiki_helpers import *
from tabulate import tabulate

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

size_compare = 'output_files/wsmall_sizes.csv'
status_csv = 'output_files/wsmalln_statuses.csv'
status2_csv = 'output_files/wsmalln_statuses2.csv'


def humansize(nbytes):
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    t = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (t, suffixes[i])


def get_sizes():
    if os.path.exists(size_compare):
        out = defaultdict(dict)
        small_list, _ = read_pickle('pickled/wsmall.pickle')
        for f in small_list:
            size = os.path.getsize(f)
            out[os.path.basename(f)]['oldf_sizeh'] = humansize(size)
            out[os.path.basename(f)]['oldf_size'] = size
            out[os.path.basename(f)]['newf_size'] = -1
            out[os.path.basename(f)]['newf_sizeh'] = -1
        tidy = tidy_uris(small_list)
        for it in tidy:
            try:
                size = os.path.getsize(wsmall_latest_p % it['original'])
                out[it['original']]['newf_size'] = size
                out[it['original']]['newf_sizeh'] = humansize(size)
            except:
                continue
        with open(size_compare, 'w') as sout:
            sout.write('old_size,old_sizeh,new_size,new_sizeh,dif,idx\n')
            c = 0
            difm = 0
            for wfile, sizes in out.items():
                print(wfile, sizes)
                if sizes['newf_size'] == -1:
                    dif = -sizes['oldf_size']
                else:
                    dif = sizes['newf_size'] - sizes['oldf_size']
                difm += dif
                sout.write('%d,%s,%d,%s,%d,%d\n' % (
                    sizes['oldf_size'], sizes['oldf_sizeh'], sizes['newf_size'], sizes['newf_sizeh'], dif, c))
                c += 1
            print(difm / c, humansize(difm / c))


def statuses_to_csv():
    if os.path.exists(status_csv):
        with open(status_csv, 'w') as sout, open(status2_csv, 'w') as sout2:
            sout.write('link,domain,suffix,idx,status\n')
            sout2.write('link,domain,suffix,idx,status\n')
            statuses = read_pickle(wsmall_latest_nwl_status)
            c = 0
            for link, status in statuses.items():
                tld = tldextract.extract(link)
                if status == -1:
                    sout2.write('%s,%s,%s,%d,%s\n' % (link, tld.domain, tld.suffix, c, 'timedout'))
                elif status == -2:
                    sout2.write('%s,%s,%s,%d,%s\n' % (link, tld.domain, tld.suffix, c, 'ip'))
                else:
                    sout.write('%s,%s,%s,%d,%d\n' % (link, tld.domain, tld.suffix, c, status))
                c += 1
    statuses = read_pickle(wsmall_latest_nwl_status)
    with open('output_files/status_count.table', 'w') as out:
        c = Counter()
        for link, status in statuses.items():
            if status == -1:
                c['timedout'] += 1
            elif status == -2:
                c['ip'] += 1
            else:
                c[status] += 1
        headers = ['status', 'count']
        data = []

        for k, v in c.items():
            data.append([k, v])
        out.write(tabulate(data, headers=headers, tablefmt='latex'))


def combine_vocab():
    with open('output_files/wsmall-vocabn.csv', 'r') as wnv, open('output_files/wsmall-vocab.csv', 'r') as wov, \
            open('output_files/wsmall-vocab-combines.csv', 'w') as wvc:
        wvc.write('wc,vc,which\n')
        for row in csv.DictReader(wnv):
            wvc.write('%s,%s,%s\n' % (row['wc'], row['vc'], 'Live Web'))
        for row in csv.DictReader(wov):
            wvc.write('%s,%s,%s\n' % (row['wc'], row['vc'], 'Data Set'))


if __name__ == '__main__':
    pass

# w_statues = dl_pages(tidy)
# link_df = get_link_df()
# nwsmall_dinfo = get_link_df()
# owsmall_ls = get_oldl_df()
# print(nwsmall_dinfo[nwsmall_dinfo.href.map(lambda x: os.path.basename(x)).isin(owsmall_ls.wsmall_file)])

# print(owsmall_ls[owsmall_ls.wsmall_file == 'Die'])

# # 4 40343.0



# for d in domains:
#     print(d)
# print(no_rel_links.size)
