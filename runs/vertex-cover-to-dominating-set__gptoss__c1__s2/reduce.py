"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) instance format is:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1.

The target problem (DominatingSet) uses the same format.

We implement the classic polynomial‑time reduction that subdivides every
edge of the input graph.  For each edge (u, v) we introduce a new vertex w
and connect it to u and v.  The resulting graph G' has the property that a
 dominating set of size ≤ k in G' exists iff the original graph G has a
 vertex cover of size ≤ k.

Isolated vertices (vertices with degree 0) are irrelevant for Vertex Cover –
they never need to be selected.  However, in a Dominating Set instance an
isolated vertex would have to be chosen, which would break the equivalence.
Therefore we simply discard isolated vertices from the construction.  If the
original instance contains no edges at all, the Vertex Cover answer is *yes*
for every k ≥ 0 (and *no* for k < 0).  To preserve this behaviour we map such
instances to the empty graph (n = 0), which is a yes‑instance of Dominating
Set for any k ≥ 0.

The reduction runs in time linear in the size of the input graph and thus
is polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys `"n"`, `"edges"` and `"k"` representing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A Dominating Set instance that is a yes‑instance exactly when the
        input is a yes‑instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑free graphs: map to the empty graph.  The empty graph is a yes‑
    # instance of Dominating Set for any k ≥ 0, matching the behaviour of
    # Vertex Cover (which is always yes when there are no edges).
    if not edges:
        return {"n": 0, "edges": [], "k": k}

    # Compute degree of each vertex to identify isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    # Map non‑isolated original vertices to a compact index space.
    old_to_new: Dict[int, int] = {}
    next_index = 0
    for v in range(n):
        if degree[v] > 0:
            old_to_new[v] = next_index
            next_index += 1

    # Number of vertices that survive (those incident to at least one edge).
    current_n = next_index
    new_edges: List[List[int]] = []

    # For each original edge, create a new subdivision vertex and connect it
    # to the (renamed) endpoints.
    for u, v in edges:
        # Both endpoints have degree > 0, so they are present in the mapping.
        u_new = old_to_new[u]
        v_new = old_to_new[v]
        # Index for the new subdivision vertex.
        w = current_n
        current_n += 1
        new_edges.append([u_new, w])
        new_edges.append([v_new, w])

    return {"n": current_n, "edges": new_edges, "k": k}

