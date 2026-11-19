"""Reduction from Vertex Cover to Dominating Set.

Given a graph G = (V, E) and integer k for Vertex Cover, we construct a graph G'
and integer k' for Dominating Set such that G has a vertex cover of size ≤ k iff G'
has a dominating set of size ≤ k'.

Construction:
1. For each edge (u, v) ∈ E create a new *edge vertex* e_{uv} adjacent only to u and v.
2. Add a *universal vertex* s adjacent to every original vertex in V (but not to any edge vertex).
3. Add a leaf ℓ attached to s (edge (s, ℓ)).
4. Set k' = k + 1 (the universal vertex s must be in any feasible dominating set
   because ℓ can only be dominated by s).

Correctness:
- In any dominating set D' of size ≤ k' the leaf ℓ forces s ∈ D' (otherwise ℓ is undominated).
- With s ∈ D', all original vertices are already dominated (by s). The remaining
  vertices of D' must dominate each edge vertex e_{uv}; the only neighbours of e_{uv}
  are u and v, so D' \ {s} contains at least one endpoint of each edge – i.e. a
  vertex cover of G of size ≤ k.
- Conversely, given a vertex cover C of G with |C| ≤ k, the set C ∪ {s} dominates all
  vertices of G': s dominates all original vertices and the leaf, while every
  edge vertex is adjacent to at least one endpoint in C. Hence a dominating set
  of size ≤ k+1 exists.

The construction runs in linear time.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import VertexCover, DominatingSet


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A valid Vertex Cover instance.

    Returns
    -------
    dict
        An equivalent Dominating Set instance.
    """
    # Validate the source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Build graph G'.
    new_edges: List[List[int]] = []
    next_id = n  # first fresh id for edge vertices

    # Edge vertices connected to their endpoints.
    for u, v in edges:
        e_id = next_id
        next_id += 1
        new_edges.append([u, e_id])
        new_edges.append([v, e_id])

    # Universal vertex s.
    universal = next_id
    next_id += 1
    for u in range(n):
        new_edges.append([u, universal])

    # Leaf attached to universal.
    leaf = next_id
    next_id += 1
    new_edges.append([universal, leaf])

    new_n = next_id
    k_prime = k + 1

    reduced_instance = {"n": new_n, "edges": new_edges, "k": k_prime}
    # Validate the target instance.
    DominatingSet.validate(reduced_instance)
    return reduced_instance

