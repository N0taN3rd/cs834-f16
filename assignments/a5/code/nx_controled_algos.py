import networkx as nx
import numpy as np
import scipy


def hits(g, max_iter=5, normalized=True, tol=1.0e-6, nstart=None, ):
    if nstart is None:
        h = dict.fromkeys(g, 1.0 / g.number_of_nodes())
    else:
        h = nstart
        # normalize starting vector
        s = 1.0 / sum(h.values())
        for k in h:
            h[k] *= s
    i = 0
    while True:  # power iteration: make up to max_iter iterations
        hlast = h
        h = dict.fromkeys(hlast.keys(), 0)
        a = dict.fromkeys(hlast.keys(), 0)
        # this "matrix multiply" looks odd because it is
        # doing a left multiply a^T=hlast^T*g
        for n in h:
            for nbr in g[n]:
                a[nbr] += hlast[n] * g[n][nbr].get('weight', 1)
        # now multiply h=ga
        for n in h:
            for nbr in g[n]:
                h[n] += a[nbr] * g[n][nbr].get('weight', 1)
        # normalize vector
        s = 1.0 / max(h.values())
        for n in h: h[n] *= s
        # normalize vector
        s = 1.0 / max(a.values())
        for n in a: a[n] *= s
        # check convergence, l1 norm
        err = sum([abs(h[n] - hlast[n]) for n in h])
        if err < tol:
            break
        if i > max_iter:
            break
        i += 1
    if normalized:
        s = 1.0 / sum(a.values())
        for n in a:
            a[n] *= s
        s = 1.0 / sum(h.values())
        for n in h:
            h[n] *= s
    return h, a


def hits_scipy(G, max_iter=100, tol=1.0e-6, normalized=True):
    M = nx.to_scipy_sparse_matrix(G, nodelist=G.nodes())
    (n, m) = M.shape  # should be square
    A = M.T * M  # authority matrix
    x = scipy.ones((n, 1)) / n  # initial guess
    # power iteration on authority matrix
    i = 0
    while True:
        xlast = x
        x = A * x
        x = x / x.max()
        # check convergence, l1 norm
        err = scipy.absolute(x - xlast).sum()
        if err < tol:
            break
        if i > max_iter:
            break
        i += 1

    a = np.asarray(x).flatten()
    # h=M*a
    h = np.asarray(M * a).flatten()
    if normalized:
        h = h / h.sum()
        a = a / a.sum()
    h = dict(zip(G.nodes(), map(lambda x: '%.2f' % float(x), h)))
    a = dict(zip(G.nodes(), map(lambda x: '%.2f' % float(x), a)))
    return h, a


def pagerank_scipy(G, alpha=0.85, personalization=None,
                   max_iter=100, tol=1.0e-6, weight='weight',
                   dangling=None):
    N = len(G)
    if N == 0:
        return {}

    nodelist = G.nodes()
    M = nx.to_scipy_sparse_matrix(G, nodelist=nodelist, weight=weight,
                                  dtype=float)
    S = scipy.array(M.sum(axis=1)).flatten()
    S[S != 0] = 1.0 / S[S != 0]
    Q = scipy.sparse.spdiags(S.T, 0, *M.shape, format='csr')
    M = Q * M

    # initial vector
    x = scipy.repeat(1.0 / N, N)

    # Personalization vector
    if personalization is None:
        p = scipy.repeat(1.0 / N, N)
    else:
        missing = set(nodelist) - set(personalization)
        if missing:
            raise nx.NetworkXError('Personalization vector dictionary '
                                   'must have a value for every node. '
                                   'Missing nodes %s' % missing)
        p = scipy.array([personalization[n] for n in nodelist],
                        dtype=float)
        p = p / p.sum()

    # Dangling nodes
    if dangling is None:
        dangling_weights = p
    else:
        missing = set(nodelist) - set(dangling)
        if missing:
            raise nx.NetworkXError('Dangling node dictionary '
                                   'must have a value for every node. '
                                   'Missing nodes %s' % missing)
        # Convert the dangling dictionary into an array in nodelist order
        dangling_weights = scipy.array([dangling[n] for n in nodelist],
                                       dtype=float)
        dangling_weights /= dangling_weights.sum()
    is_dangling = scipy.where(S == 0)[0]

    # power iteration: make up to max_iter iterations
    for _ in range(max_iter):
        xlast = x
        x = alpha * (x * M + sum(x[is_dangling]) * dangling_weights) + \
            (1 - alpha) * p
        return dict(zip(nodelist, map(lambda x: '%.2f' % float(x), x)))
