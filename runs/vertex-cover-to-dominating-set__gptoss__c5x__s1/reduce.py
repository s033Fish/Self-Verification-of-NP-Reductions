"""Reduction from Vertex Cover to Dominating Set.

Construction:
Given G = (V, E) with n = |V|, build G' as follows:
  * For each vertex v ∈ V add a leaf ℓ_v adjacent only to v.
  * For each edge (u, v) ∈ E add a new vertex e_{uv} adjacent to u and v.
The vertex set of G' is V ∪ {ℓ_v} ∪ {e_{uv}}.
Let iso be the number of isolated vertices in G (vertices with degree 0).
Set k' = k + iso.

Correctness:
*If C ⊆ V is a vertex cover of G with |C| ≤ k, then D = C ∪ {ℓ_v : v ∉ C} dominates G'.
  Every leaf ℓ_v is dominated (by itself if v ∉ C, otherwise by v ∈ C). Every edge‑vertex e_{uv} is adjacent to u or v, which lies in C, so it is dominated.
  The size of D is |C| + (n‑|C|) = n, but we can replace leaves of isolated vertices by the isolated vertex itself, reducing the size by 1 for each isolated vertex. Hence |D| = k + iso = k'.
*Conversely, let D be a dominating set of G' with |D| ≤ k'. Any leaf ℓ_v in D can be replaced by its neighbor v without increasing size. After this replacement we obtain a set C ⊆ V of size ≤ k'‑iso = k that dominates all edge‑vertices, which means for each edge (u, v) at least one endpoint is in C. Thus C is a vertex cover of G of size ≤ k.
Therefore G has a vertex cover of size ≤ k iff G' has a dominating set of size ≤ k'.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    VertexCover.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # count isolated vertices
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    iso = sum(1 for d in degree if d == 0)

    new_edges: List[List[int]] = []
    # leaf vertices
    for v in range(n):
        leaf = n + v
        new_edges.append([leaf, v])
    # edge vertices
    for idx, (u, v) in enumerate(edges):
        ev = 2 * n + idx
        new_edges.append([ev, u])
        new_edges.append([ev, v])

    reduced_instance = {
        "n": 2 * n + len(edges),
        "edges": new_edges,
        "k": k + iso,
    }
    DominatingSet.validate(reduced_instance)
    return reduced_instance

