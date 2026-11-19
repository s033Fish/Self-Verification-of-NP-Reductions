"""Polynomial-time reduction from Vertex Cover to Set Cover.

Given a Vertex Cover instance {"n": n, "edges": [[u, v], ...], "k": k},
build a Set Cover instance as follows:

* The universe has one element per edge of the graph.
* For every vertex v, create one set containing exactly the elements
  (edges) incident to v.

A set of vertices covers every edge of the graph if and only if the
corresponding collection of sets covers the whole universe, so the
minimum cover sizes are equal.  Hence the answer is preserved with the
same budget k.

The construction uses O(n + m) time and space, where m is the number of
edges, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to a Set Cover instance.

    The returned instance is
        {"universe_size": m, "sets": [...], "k": k}
    where m is the number of edges and set i contains the indices of all
    edges incident to vertex i.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge.
    universe_size = len(edges)

    # For each vertex, collect the indices of its incident edges.
    sets = [[] for _ in range(n)]
    for edge_index, edge in enumerate(edges):
        u, v = edge[0], edge[1]
        sets[u].append(edge_index)
        sets[v].append(edge_index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
