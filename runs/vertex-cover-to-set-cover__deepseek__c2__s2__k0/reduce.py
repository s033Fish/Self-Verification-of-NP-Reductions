"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction: let the universe be the set of edges 0..m-1.  For every
vertex v, create one set containing the indices of all edges incident to
v.  Choosing a collection of sets that covers the universe is exactly
choosing a set of vertices that covers every edge, and the number of
chosen sets equals the number of chosen vertices.  Hence the graph has a
vertex cover of size at most k iff the constructed set system has a set
cover of size at most k.

Edge cases:
  * k < 0: the source is no; we keep k < 0, so the target is no too.
  * no edges (m = 0): the universe is empty, which is yes for every
    k >= 0, matching the source.
  * k >= n: all vertex-sets together cover every edge, so the target is
    yes, matching the source.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Universe element i corresponds to edges[i].
    universe_size = len(edges)

    # sets[v] = indices of edges incident to vertex v.
    sets = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
