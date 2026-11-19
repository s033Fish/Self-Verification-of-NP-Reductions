"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source (Vertex Cover):  {"n": n, "edges": [[u, v], ...], "k": k}
Target (Dominating Set): {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and |E| = m, build a
Dominating Set instance G' as follows:

  * Keep every original vertex 0..n-1.
  * For each edge e = (u, v) in E, add a brand new vertex x_e (numbered
    n, n+1, ..., n+m-1) and connect it to both u and v.
  * Keep the original edges (u, v) as well.

Correctness
-----------
Let iso be the number of isolated vertices of G (vertices of degree 0).

Claim: min dominating set size of G' = min vertex cover size of G + iso.

Upper bound: if C is a minimum vertex cover of G, then C together with all
isolated vertices of G is a dominating set of G'.  Every original vertex is
either in the set, isolated (hence in the set), or has an incident edge whose
other endpoint lies in C.  Every added vertex x_e is adjacent to an endpoint
of e that lies in C.

Lower bound: let D be a dominating set of G'.  Every isolated vertex of G
must be in D.  For each edge e = (u, v), x_e is dominated, so x_e, u or v is
in D; replacing each x_e in D by one of its endpoints yields a vertex cover
of G of size at most |D| - iso.  Hence |D| >= minVC(G) + iso.

Therefore G has a vertex cover of size at most k (k >= 0) iff G' has a
dominating set of size at most k + iso.  For k < 0 the source is always "no",
so we return k' = -1, which is always "no" for the target as well.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Count isolated vertices of the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    iso = sum(1 for d in degree if d == 0)

    # Build the target graph: original edges plus, for each edge, a new
    # vertex adjacent to both endpoints.
    new_edges = [list(e) for e in edges]
    for i, (u, v) in enumerate(edges):
        x = n + i
        new_edges.append([u, x])
        new_edges.append([v, x])

    new_n = n + len(edges)

    if k < 0:
        new_k = -1
    else:
        new_k = k + iso

    return {"n": new_n, "edges": new_edges, "k": new_k}
