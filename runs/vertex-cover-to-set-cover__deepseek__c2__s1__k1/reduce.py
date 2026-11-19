"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Set Cover):
    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction:
    * The universe is the set of edges of the graph (edge i <-> element i).
    * For every vertex v in 0..n-1 we create one set containing exactly the
      indices of the edges incident to v (isolated vertices yield empty sets).
    * k is kept unchanged.

Correctness:
    A set of vertices covers every edge (i.e. is a vertex cover) iff the
    corresponding collection of vertex-sets contains every element of the
    universe (i.e. is a set cover).  Hence a vertex cover of size <= k exists
    iff a set cover of size <= k exists.  The edge cases line up: k < 0 is
    "no" for both; an edgeless graph gives u = 0, which is "yes" for every
    k >= 0; and k >= n is "yes" for both since all vertex-sets cover the
    whole universe.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # element i of the universe corresponds to edge edges[i]
    sets = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        sets[u].append(i)
        sets[v].append(i)

    return {"universe_size": len(edges), "sets": sets, "k": k}
