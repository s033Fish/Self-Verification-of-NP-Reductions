"""Polynomial-time reduction from Clique to Vertex Cover.

Clique instance: (G, k).  Let G' be the complement of G (same vertex set,
edges exactly the non-edges of G).  A set S is a clique in G iff S is an
independent set in G'.  A set C is a vertex cover of G' iff its complement
V \ C is an independent set of G'.  Hence

    G has a clique of size >= k
      <=> G' has an independent set of size >= k
      <=> G' has a vertex cover of size <= n - k.

So the reduction maps (G, k) to (G', n - k).  The construction is polynomial
in the size of the instance (it only builds the complement graph).
"""


def reduce(instance):
    """Map a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}

    The output graph is the complement of the input graph: it has the same
    vertices 0..n-1 and contains exactly the pairs that are NOT edges of the
    input graph.  The target budget is n - k.
    """
    n = instance["n"]
    k = instance["k"]

    # Build a set of the undirected edges of the input graph, normalizing
    # each pair so that [u, v] and [v, u] are treated as the same edge.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Complement edges: all u < v that are not present in the input graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
