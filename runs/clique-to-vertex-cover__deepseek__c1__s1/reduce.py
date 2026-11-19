"""Polynomial-time reduction from Clique to Vertex Cover.

A set S is a clique in G iff V \\ S is a vertex cover in the complement
graph complement(G).  Hence G has a clique of size at least k iff
complement(G) has a vertex cover of size at most n - k.

The reduction therefore maps (G, k) to (complement(G), n - k).  It runs in
polynomial time (in fact O(n^2)) and does not call any solver.
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}

    where the output edges are exactly the non-edges of the input graph
    (the complement graph on the same vertex set).
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges so each undirected edge is stored once.
    present = set()
    for u, v in instance["edges"]:
        if u == v:
            # Self-loops are not valid edges in either problem; ignore them.
            continue
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement graph: every non-edge of the input becomes an edge.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
