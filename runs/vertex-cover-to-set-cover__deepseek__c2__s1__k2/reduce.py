"""Polynomial-time reduction from Vertex Cover to Set Cover.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
Set Cover instance:    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction: let the universe be the set of edges (edge i is element i).
For every vertex v, create one set containing all edges incident to v.
Choosing at most k vertices that cover every edge is exactly choosing at
most k of these sets whose union is the whole universe.  So the answer is
preserved.  The construction takes O(n + m) time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Element i of the universe corresponds to edges[i].
    incident = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        incident[u].append(i)
        incident[v].append(i)

    return {
        "universe_size": len(edges),
        "sets": incident,
        "k": k,
    }
