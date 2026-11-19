"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Set Cover):
    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Construction:
    * One universe element per edge of the graph.
    * One set per vertex, containing exactly the edges incident to it.
    * Keep the same budget k.

A set of vertices covers every edge (i.e. is a vertex cover of size <= k)
if and only if the corresponding collection of sets covers every element
(i.e. is a set cover of size <= k).  The construction uses O(n + m) time
and space, hence is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # sets[v] = list of edge indices incident to vertex v
    sets = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        sets[u].append(idx)
        sets[v].append(idx)

    return {
        "universe_size": len(edges),
        "sets": sets,
        "k": k,
    }
