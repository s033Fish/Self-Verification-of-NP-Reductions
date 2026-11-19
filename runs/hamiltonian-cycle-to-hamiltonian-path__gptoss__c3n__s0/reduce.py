"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

Given an undirected graph G = (V, E) we construct a graph G' as follows:
1. Choose an arbitrary edge (a, b) from E.  (If E is empty, the answer is
   trivially ``no`` and we map to a known ``no`` instance.)
2. Remove the edge (a, b) from the edge set.
3. Add two new vertices s and t (indices |V| and |V|+1) and add edges (s, a)
   and (t, b).
The resulting graph G' has |V|+2 vertices.

Correctness:
*If* G has a Hamiltonian cycle, break the cycle at the edge (a, b).  The
remaining walk visits all original vertices exactly once and starts at b and ends
at a.  Adding the edges (s, a) at the start and (t, b) at the end yields a
Hamiltonian path in G' from s to t.
*Conversely*, any Hamiltonian path in G' must start at s and end at t because
s and t have degree 1.  Removing s, t and reinstating the edge (a, b) gives a
Hamiltonian cycle in G.

The construction runs in linear time and respects all edge‑case specifications.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianCycle, HamiltonianPath


def reduce(instance: Dict) -> Dict:
    """Reduce Hamiltonian‑Cycle to Hamiltonian‑Path.

    Parameters
    ----------
    instance: dict
        Graph instance for :class:`HamiltonianCycle`.

    Returns
    -------
    dict
        Graph instance for :class:`HamiltonianPath` that is yes exactly when the
        input instance is yes.
    """
    # Validate source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial cases where the source answer is always ``no``.
    if n <= 2:
        empty = {"n": 0, "edges": []}
        HamiltonianPath.validate(empty)
        return empty

    # If there is no edge, a Hamiltonian cycle cannot exist.
    if not edges:
        empty = {"n": 0, "edges": []}
        HamiltonianPath.validate(empty)
        return empty

    # Choose an arbitrary edge (a, b).
    a, b = edges[0]

    # Build new edge list: copy all edges except (a, b).
    new_edges: List[List[int]] = []
    for u, v in edges:
        if (u == a and v == b) or (u == b and v == a):
            continue
        new_edges.append([u, v])

    # Add two new vertices s and t.
    s = n          # index for new start vertex
    t = n + 1      # index for new end vertex
    new_n = n + 2

    # Connect s to a and t to b.
    new_edges.append([s, a])
    new_edges.append([t, b])

    reduced_instance = {"n": new_n, "edges": new_edges}
    HamiltonianPath.validate(reduced_instance)
    return reduced_instance

