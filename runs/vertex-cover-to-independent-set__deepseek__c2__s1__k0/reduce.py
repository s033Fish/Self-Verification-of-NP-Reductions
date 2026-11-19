"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G = (V, E) if and only if V \ S is an
independent set of G.  Consequently G has a vertex cover of size at most k
if and only if G has an independent set of size at least n - k.

Therefore the reduction maps a Vertex Cover instance

    {"n": n, "edges": [[u, v], ...], "k": k}

to the Independent Set instance

    {"n": n, "edges": [[u, v], ...], "k": n - k}.

This is a valid polynomial-time many-one reduction.  It also respects the
documented edge cases:
  * k < 0            -> target k' = n - k > n, which is always no;
  * k >= n           -> target k' = n - k <= 0, which is always yes;
  * edgeless graph   -> every subset is independent, so the target is yes
                        for every k' <= n (and k' <= 0 is yes as well).
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
