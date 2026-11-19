"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source (Vertex Cover):   {"n": n, "edges": [[u, v], ...], "k": k}
Target (Dominating Set): {"n": n', "edges": [[u, v], ...], "k": k'}

Construction
------------
Let G = (V, E) be the source graph with |V| = n and |E| = m.

Build G' as follows:
  * Keep every original vertex 0..n-1 and every original edge.
  * For each edge e_i = [u, v] (i = 0..m-1) add a new "edge vertex" n+i
    together with the two edges [n+i, u] and [n+i, v].
  * Let iso be the number of isolated vertices of G (degree 0).
  * Set k' = k + iso.

Correctness
-----------
Every edge vertex x_e has closed neighbourhood {x_e, u, v}.  In any
dominating set D of G' we may replace x_e by one of its endpoints u (if
neither endpoint is in D) without losing domination, so some minimum
dominating set D* contains only original vertices.  Then for each edge e
at least one endpoint lies in D*, i.e. D* is a vertex cover of G, and D*
must also contain every isolated vertex of G (isolated vertices stay
isolated in G').  Hence |D*| >= minVC(G) + iso.

Conversely, if C is a minimum vertex cover of G (which never needs to
contain isolated vertices), then C together with all isolated vertices
dominates G': every non-isolated original vertex has an incident edge
whose endpoint is in C, every edge vertex has an endpoint in C, and the
isolated vertices are included.  Hence minDS(G') <= minVC(G) + iso.

Therefore minDS(G') = minVC(G) + iso, and so
    VC(G) <= k   <=>   DS(G') <= k + iso,
which is exactly the required yes/no equivalence.  The construction is
polynomial (O(n + m) new vertices/edges) and uses no solvers.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degrees of the original vertices, used to count isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    iso = sum(1 for d in degree if d == 0)

    m = len(edges)
    new_edges = [list(edge) for edge in edges]

    # One new vertex per original edge, adjacent to both endpoints.
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([w, u])
        new_edges.append([w, v])

    return {
        "n": n + m,
        "edges": new_edges,
        "k": k + iso,
    }
