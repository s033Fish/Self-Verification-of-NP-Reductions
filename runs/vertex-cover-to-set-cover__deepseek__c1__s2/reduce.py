"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Set Cover):
    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction
------------
Create one universe element for each edge of the graph. For every vertex v
create a set containing the indices of all edges incident to v.

A collection of vertex-sets covers the universe (every edge element) exactly
when the corresponding vertices touch every edge, i.e. form a vertex cover.
Therefore the minimum vertex cover size equals the minimum set cover size,
and the yes/no answer is preserved for the same value of k.

The construction runs in O(n + |edges|) time and produces an instance whose
size is polynomial in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One universe element per edge.
    universe_size = len(edges)

    # sets[v] = indices of the edges incident to vertex v.
    sets = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": universe_size, "sets": sets, "k": k}
