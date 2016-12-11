from nx_controled_algos import *
from contextClasses import GraphBuilder, AutoSLatexTable, AutoSaveCsv, AutoSaveTwoFileTypes

node_filep = 'data/graph_nodes.txt'
node_config = {'how_read': 'one_line', 'sep': ' '}
edge_filep = 'data/graph_edges.csv'
edges_config = {'how_read': 'csv', 'csv_mapping': {'node': 'node', 'edge': 'edge'}}

iter_tablep = 'output_files/q1_iteration%d.txt'
iter_csvp = 'output_files/q1_iteration%d.csv'


def do_sort(items):
    return sorted(items, key=lambda x: int(x[0]))


def do_zip(h, a, p):
    return zip(do_sort(h.items()), do_sort(a.items()), do_sort(p.items()))


if __name__ == '__main__':
    with GraphBuilder(node_filep, edge_filep, node_config, edges_config, graph_type='d') as g:
        csv_header = ['iter', 'node', 'hs', 'as', 'pr']
        table_header = ['Iteration', 'Node', 'Hub Score', 'Authority Score', 'PageRank']
        for i in range(1, 6, 1):
            print('iteration %d' % i)
            hubs, authorities = hits_scipy(g, max_iter=i - 1)
            pr = pagerank_scipy(g, max_iter=i)
            args = {'f_clazz': AutoSLatexTable, 'f_filep': iter_tablep % i, 'f_type': list, 'f_fn': table_header,
                    's_clazz': AutoSaveCsv, 's_filep': iter_csvp % i,
                    's_fn': csv_header, 's_type': list}
            with AutoSaveTwoFileTypes(**args) as (ltbl, csv):
                for ((hubn, hs), (authn, auths), (prn, prs)) in do_zip(hubs, authorities, pr):
                    print('node %s, hub score=%s, authority score=%s, pagerank score=%s' % (hubn, hs, auths, prs))
                    csv.append({'iter': i, 'node': hubn, 'hs': hs, 'as': auths, 'pr': prs})
                    ltbl.append([i, hubn, hs, auths, prs])
                print('----------------------------------------\n')
