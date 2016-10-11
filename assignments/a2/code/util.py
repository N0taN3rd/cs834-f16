import pickle
import networkx as nx

wlarge = 'pickled/wiki-large.pickle'
wlarge2 = 'pickled/wiki-large2.pickle'

wlarge_edges = 'pickled/wiki-large-sl.pickle'
wlarge_edges2 = 'pickled/wiki-large-edges2.pickle'
wlarge_edges3 = 'pickled/wiki-large-edges3.pickle'

wlarge_graph = 'pickled/wiki-large-graph.pickle'
wlarge_graph2 = 'pickled/wiki-large-graph2.pickle'
wlarge_graph3 = 'pickled/wiki-large-graph3.pickle'

wsmall = 'pickled/wiki-small.pickle'
wsmall2 = 'pickled/wiki-small2.pickle'

wsmall_edges = 'pickled/wiki-small-edges.pickle'
wsmall_edges2 = 'pickled/wiki-small-edges2.pickle'
wsmall_edges3 = 'pickled/wiki-small-edges3.pickle'

wsmall_graph = 'pickled/wiki-small-graph.pickle'
wsmall_graph2 = 'pickled/wiki-small-graph2.pickle'
wsmall_graph3 = 'pickled/wiki-small-graph3.pickle'


def dump_pickle(obj, file):
    with open(file, 'wb') as out:
        pickle.dump(obj, out)


def read_pickle(name):
    with open(name, "rb") as input_file:
        return pickle.load(input_file)


def small():
    edges = read_pickle(wsmall_edges)  # type: list[tuple[str, list[tuple[str,str]]]]
    graph = nx.DiGraph()
    for n, e in edges:
        graph.add_node(n)
    for n, e in edges:
        if len(e) == 0:
            continue
        else:
            for nn, ee in e:
                graph.add_edge(nn, ee)

    # for n in graph.nodes():
    #     print(graph.in_edges(n))
    print(graph.number_of_nodes())

if __name__ == '__main__':
    small()
    graph, pagerank = read_pickle('pickled/wiki-small-graph.pickle')  # type: tuple[nx.DiGraph, dict]
    inlinks = []
    for n in graph.nodes():
        ins = graph.in_edges(n)
        if len(ins) > 0:
            inlinks.append((n,ins))
    print(len(inlinks))


