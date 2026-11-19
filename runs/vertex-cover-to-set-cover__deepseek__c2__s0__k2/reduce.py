"""Polynomial-time reduction from Vertex Cover to Set Cover.

Given a Vertex Cover instance ``{"n": n, "edges": [[u, v], ...], "k": k}``,
build a Set Cover instance whose universe is the set of edges and which has
one set per vertex, containing exactly the edges incident to that vertex.

A set of vertices covers every edge iff the corresponding collection of
sets covers the whole universe, so the minimum cover sizes coincide and the
"at most k" answers agree.  The construction is linear in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge.
    universe_size = len(edges)

    # sets[v] = indices of the edges incident to vertex v.
    sets = [[] for _ in range(n)]
    for edge_index, (u, v) in enumerate(edges):
        sets[u].append(edge_index)
        sets[v].append(edge_index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
