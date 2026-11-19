"""Polynomial-time reduction from Vertex Cover to Set Cover.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
Set Cover instance:    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction:
  * The universe is the set of edges; edge i is element i.
  * For every vertex v there is one set S_v containing the indices of all
    edges incident to v.
  * k is unchanged.

A collection of at most k sets covers every edge-element iff the
corresponding vertices form a vertex cover of size at most k.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Element i corresponds to edge i.
    universe_size = len(edges)
    sets = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        sets[u].append(i)
        sets[v].append(i)

    return {"universe_size": universe_size, "sets": sets, "k": k}
