"""Polynomial-time reduction from Independent Set to Vertex Cover.

The complement of a vertex cover is an independent set, and vice versa:
for any graph on n vertices,

    C is a vertex cover  <=>  V \\ C is an independent set.

Therefore the minimum vertex cover size equals n minus the maximum
independent set size.  An Independent Set instance (G, k) is a yes
instance (there is an independent set of size >= k) exactly when the
same graph has a vertex cover of size <= n - k.  So the reduction keeps
the graph unchanged and maps k to n - k.

Edge cases line up automatically:
  * k <= 0  (IS always yes)  maps to n - k >= n, and any graph has a
    vertex cover of size <= n (all vertices), so VC is yes.
  * k > n   (IS always no)   maps to n - k < 0, and VC with a negative
    budget is always no.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input / output format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
