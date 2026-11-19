"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

Standard reduction: pick a distinguished vertex (we use 0). Remove it and add two new
vertices s and t, connecting each of them to every former neighbor of 0. The
resulting graph has a Hamiltonian path from s to t iff the original graph has a
Hamiltonian cycle.

Edge cases: for n <= 2 the source problem is always NO, so we map to a trivially
NO Hamiltonian‑Path instance (empty graph).
"""

from __future__ import annotations

from typing import Dict, List, Set

def reduce(instance: Dict) -> Dict:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # n <= 2: always NO for Hamiltonian Cycle
    if n <= 2:
        return {"n": 0, "edges": []}

    # Determine neighbors of vertex 0
    neighbor_set: Set[int] = set()
    for u, v in edges:
        if u == 0:
            neighbor_set.add(v)
        elif v == 0:
            neighbor_set.add(u)
    # New vertex count: (n-1) original vertices (excluding 0) + 2 leaves = n+1
    new_n = n + 1
    s = n - 1  # first new vertex index
    t = n      # second new vertex index
    new_edges: List[List[int]] = []
    seen = set()
    def add(u: int, v: int) -> None:
        if u == v:
            return
        key = (min(u, v), max(u, v))
        if key not in seen:
            seen.add(key)
            new_edges.append([u, v])

    # Map original vertices (except 0) to new indices: old i -> i-1
    def map_vertex(old: int) -> int:
        return old - 1  # old != 0 guaranteed

    # Add edges among original vertices (excluding any incident to 0)
    for u, v in edges:
        if u == 0 or v == 0:
            continue
        add(map_vertex(u), map_vertex(v))

    # Connect s and t to each neighbor of 0
    for w in neighbor_set:
        new_w = map_vertex(w)
        add(s, new_w)
        add(t, new_w)

    return {"n": new_n, "edges": new_edges}

