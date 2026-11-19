"""Reduction from Vertex Cover to Dominating Set.

Given a graph G = (V, E) and integer k (Vertex Cover instance), we build a graph
G' = (V', E') for the Dominating Set problem as follows:
  * V' contains all original vertices V.
  * For each edge e = (u, v) ∈ E we add a new vertex x_e and edges (x_e, u) and
    (x_e, v).
  * We add one additional vertex s (the "universal" vertex) and connect it to
    every original vertex: edges (s, v) for all v ∈ V.
The parameter for Dominating Set is k' = k + 1.

Correctness:
  * (=>) If C ⊆ V is a vertex cover of size ≤ k, then D = C ∪ {s} has size ≤ k+1.
    The universal vertex s dominates itself and all original vertices.  For any
    edge‑vertex x_e, at least one endpoint of e lies in C, so x_e is adjacent to a
    vertex of D and is therefore dominated.  Hence D is a dominating set of
    G'.
  * (<=) Suppose D is a dominating set of G' with |D| ≤ k+1.  The universal
    vertex s cannot be omitted: if s ∉ D then each original vertex v must be
    dominated either by itself (v ∈ D) or by some edge‑vertex x_e adjacent to v.
    In the latter case, x_e also dominates the other endpoint of e, so we could
    replace x_e by that endpoint without increasing the size of D.  Repeating
    this replacement yields a dominating set D' that consists only of original
    vertices and possibly s.  Because s dominates all original vertices, we can
    remove s from D' and obtain a set C ⊆ V of size ≤ k that still dominates all
    edge‑vertices.  An edge‑vertex x_e is adjacent only to its two endpoints, so
    dominating x_e requires at least one of its endpoints to be in C.  Therefore C
    hits every edge of G, i.e., C is a vertex cover of size ≤ k.
Thus the reduction preserves the answer and runs in polynomial time.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Returns a new instance dict compatible with ``DominatingSet.validate``.
    """
    # Validate the source instance first.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    m = len(edges)
    # Index layout:
    # 0 .. n-1          : original vertices
    # n .. n+m-1        : edge vertices (one per original edge)
    # n+m               : universal vertex s
    s_index = n + m
    total_n = n + m + 1

    new_edges: List[List[int]] = []

    # Edge vertices connected to their endpoints
    for i, (u, v) in enumerate(edges):
        ev = n + i
        new_edges.append([ev, u])
        new_edges.append([ev, v])

    # Universal vertex connected to all original vertices
    for v in range(n):
        new_edges.append([s_index, v])

    reduced_instance = {
        "n": total_n,
        "edges": new_edges,
        "k": k + 1,
    }

    # Validate target instance to ensure correct format.
    DominatingSet.validate(reduced_instance)
    return reduced_instance

