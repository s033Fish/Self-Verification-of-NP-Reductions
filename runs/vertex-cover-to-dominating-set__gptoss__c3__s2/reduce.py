"""Reduction from Vertex Cover to Dominating Set.

We use the classic polynomial‑time reduction:
* For each edge (u,v) of the original graph we introduce a new *edge‑vertex*
  e_uv and connect it to u and v.
* We also add a new *universal* vertex u* that is adjacent to every original
  vertex (but not to the edge‑vertices).  The universal vertex forces a
  dominating set to contain it (or else all original vertices would have to be
  chosen individually, exceeding the allowed budget).

If the original instance has a vertex cover C of size ≤ k, then
C ∪ {u*} dominates the constructed graph: each edge‑vertex is adjacent to an
endpoint in C, and every original vertex is either in C or adjacent to u*.
Conversely, any dominating set D of size ≤ k+1 must contain u* (otherwise D would need
to contain all original vertices, which would already be >k+1 unless the graph is
trivial).  Removing u* leaves a set C = D \ {u*} of original vertices that
covers every edge, i.e. a vertex cover of size ≤ k.

Thus the reduction preserves the answer.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        Vertex Cover instance with keys "n", "edges", "k".

    Returns
    -------
    dict
        Dominating Set instance equivalent to the input.
    """
    # Validate source instance (raises if malformed).
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑vertices: one per original edge, numbered after the original vertices.
    edge_vertex_start = n
    final_edges: List[List[int]] = []
    for idx, (u, v) in enumerate(edges):
        ev = edge_vertex_start + idx
        final_edges.append([u, ev])
        final_edges.append([v, ev])

    # Universal vertex adjacent to every original vertex.
    universal_id = edge_vertex_start + len(edges)
    for v in range(n):
        final_edges.append([universal_id, v])

    n_target = universal_id + 1
    k_target = k + 1  # we need the universal vertex in the dominating set

    reduced = {"n": n_target, "edges": final_edges, "k": k_target}
    # sanity check that the target instance is well‑formed
    DominatingSet.validate(reduced)
    return reduced

