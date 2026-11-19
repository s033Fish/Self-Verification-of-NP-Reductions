"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction:
  * One universe element per edge, labelled by the edge's index.
  * One set per vertex v, containing the indices of all edges incident to v.

A set of vertices covers every edge iff the corresponding collection of sets
covers every universe element.  Hence the graph has a vertex cover of size at
most k iff the set system has a set cover of size at most k.  The reduction
preserves k exactly, so all edge cases (k < 0, no edges, k >= n) behave
correctly.  Construction time is O(n + m).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Element i corresponds to edges[i].
    universe_size = len(edges)

    # sets[v] = indices of edges incident to vertex v.
    sets = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        sets[u].append(i)
        sets[v].append(i)

    return {"universe_size": universe_size, "sets": sets, "k": k}
