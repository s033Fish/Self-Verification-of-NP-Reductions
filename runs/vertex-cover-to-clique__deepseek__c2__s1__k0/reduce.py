"""Polynomial-time reduction from Vertex Cover to Clique.

Key fact: a set S is a vertex cover of G = (V, E) iff V \ S is an
independent set in G, i.e. a clique in the complement graph G'.

Therefore G has a vertex cover of size at most k iff the complement
graph G' has a clique of size at least n - k.

Reduction: given a Vertex Cover instance {"n": n, "edges": E, "k": k},
return the Clique instance {"n": n, "edges": E', "k": n - k}, where E'
consists of exactly the non-edges of G (all pairs {u, v} with u != v
that are not in E).

This handles all edge cases:
  * k < 0: source is no; target k' = n - k > n, so target is no.
  * E empty: source is yes for k >= 0; G' is complete, so it has a
    clique of size n >= n - k = k' whenever k >= 0.
  * k >= n: source is yes; target k' = n - k <= 0, so target is yes.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Build the set of existing undirected edges, normalizing orientation.
    existing = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Complement edges: every pair not present in the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
