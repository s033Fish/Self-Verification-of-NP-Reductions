"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) expects an instance of the form
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1 and edges are undirected without duplicates.

The target problem (DominatingSet) uses the same format.  We must produce a
graph G' and an integer k' such that G has a vertex cover of size at most k
iff G' has a dominating set of size at most k'.  The classic polynomial‑time
reduction works as follows:

* For each edge e = (u, v) of the original graph, introduce a new vertex
  e' that is adjacent exactly to u and v.
* Keep the original vertices and (optionally) the original edges.
* Set k' = k.

If C is a vertex cover of G, then C dominates every original vertex (any
vertex not in C is adjacent to a vertex in C because all its incident edges
are covered) and also dominates each new edge‑vertex because at least one of
its endpoints lies in C.  Conversely, any dominating set D of G' can be
transformed into a dominating set containing only original vertices by
replacing any edge‑vertex with one of its endpoints; the resulting set is a
vertex cover of G.

The reduction above fails for edgeless graphs: a vertex cover may be empty
while a dominating set would need to contain all isolated vertices.  To
preserve equivalence we handle this special case separately by mapping an
edgeless instance to an empty graph (n = 0).  An empty graph has a dominating
set of size ≤ k exactly when k ≥ 0, which matches the vertex‑cover answer
for edgeless graphs (yes for k ≥ 0, no for k < 0).

The function ``reduce`` implements this transformation.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A dictionary representing a Dominating Set instance that is yes
        exactly when the input instance is yes.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑less graphs: map to an empty graph.  This preserves the answer for
    # all k (including negative values).
    if not edges:
        return {"n": 0, "edges": [], "k": k}

    # New vertices: one for each original edge.
    m = len(edges)
    new_n = n + m
    new_edges: List[List[int]] = []

    # Keep original edges (they are harmless for the reduction).
    new_edges.extend(edges)

    # Add edges from each edge‑vertex to its two endpoints.
    for idx, (u, v) in enumerate(edges):
        ev = n + idx  # identifier of the new vertex for this edge
        new_edges.append([u, ev])
        new_edges.append([v, ev])

    return {"n": new_n, "edges": new_edges, "k": k}

