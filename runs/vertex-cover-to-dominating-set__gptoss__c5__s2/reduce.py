"""Reduction from Vertex Cover to Dominating Set.

The standard polynomial‑time reduction works as follows.
Given a graph G = (V, E) and integer k (Vertex Cover instance), we build a
new graph G' = (V', E') and integer k' (Dominating Set instance) such that
G has a vertex cover of size ≤ k iff G' has a dominating set of size ≤ k'.

Construction:
  * Keep all original vertices V in V'.
  * For each edge (u, v) ∈ E create a fresh vertex e_{uv} and add edges
    (u, e_{uv}) and (v, e_{uv}).  These are the only edges incident to e_{uv}.
  * Add a new vertex a and a leaf vertex b.  Connect a to every original
    vertex in V and also connect a to b.
  * Set k' = k + 1.

Correctness sketch:
  * In any dominating set D' of size ≤ k' the leaf b must be dominated, and the
    only neighbour of b is a, so a ∈ D'.  Removing a leaves at most k vertices.
  * The remaining vertices of D' can only dominate the edge‑vertices e_{uv} via
    the original endpoints, because a is not adjacent to any e_{uv}.  Hence the
    set D = D' \ {a} is a vertex cover of G of size ≤ k.
  * Conversely, given a vertex cover C of size ≤ k, the set C ∪ {a} dominates
    all vertices of G': a dominates b and all original vertices, while each
    edge‑vertex e_{uv} is adjacent to u or v which lies in C.

Edge cases are handled automatically: isolated vertices are kept (they are
adjacent to a, so they are dominated).  If the original graph has no edges,
the reduction yields a graph where a dominates everything, and the answer
matches the trivial vertex‑cover answer.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        VertexCover instance with keys ``n``, ``edges`` and ``k``.

    Returns
    -------
    dict
        DominatingSet instance preserving the answer.
    """
    # Validate source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build edge list for G'.
    reduced_edges: List[List[int]] = []
    next_idx = n  # indices for new vertices start after original ones

    # Edge‑vertices for each original edge.
    for u, v in edges:
        e_idx = next_idx
        next_idx += 1
        reduced_edges.append([u, e_idx])
        reduced_edges.append([v, e_idx])

    # Add forced vertex a and its leaf b.
    a_idx = next_idx
    b_idx = next_idx + 1
    next_idx += 2

    # a adjacent to all original vertices.
    for v in range(n):
        reduced_edges.append([a_idx, v])
    # a adjacent to leaf b.
    reduced_edges.append([a_idx, b_idx])

    reduced_instance: Dict = {
        "n": next_idx,
        "edges": reduced_edges,
        "k": k + 1,
    }

    # Validate the target instance.
    DominatingSet.validate(reduced_instance)
    return reduced_instance

