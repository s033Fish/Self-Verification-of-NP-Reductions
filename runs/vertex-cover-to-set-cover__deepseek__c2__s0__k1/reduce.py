"""Polynomial-time reduction from Vertex Cover to Set Cover.

Given a Vertex Cover instance {"n": n, "edges": [[u, v], ...], "k": k},
build a Set Cover instance as follows:

* The universe has one element per edge of the graph.
* For every vertex v, create a set containing the indices of all edges
  incident to v.
* Keep the same budget k.

A set of vertices covers every edge exactly when the corresponding
collection of sets covers every universe element, so the answer is
preserved.  The construction takes O(n + m) time and space, where m is
the number of edges.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an equivalent Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element for each edge.
    universe_size = len(edges)

    # sets[v] = indices of edges incident to vertex v.
    sets = [[] for _ in range(n)]
    for edge_index, (u, v) in enumerate(edges):
        sets[u].append(edge_index)
        sets[v].append(edge_index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
