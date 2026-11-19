"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) asks whether an undirected graph
contains a cycle that visits every vertex exactly once.  The target
problem (HamiltonianPath) asks whether an undirected graph contains a
path that visits every vertex exactly once (endpoints are unrestricted).

We construct, in polynomial time, a new graph G' such that G has a
Hamiltonian cycle iff G' has a Hamiltonian path.

Construction (for |V(G)| >= 3):
  * Choose an arbitrary vertex a of G – we use vertex 0.
  * Replace a by two vertices a1 and a2.
  * Add two pendant vertices p1 and p2, each adjacent only to a1 and a2
    respectively.
  * For every edge (a, v) in G, add edges (a1, v) and (a2, v) to G'.
  * All other edges of G are kept unchanged (with vertex indices
    appropriately shifted because of the new vertices).

The resulting graph G' has n+3 vertices.  Any Hamiltonian path in G'
must start at p1 and end at p2 (they are the only degree‑1 vertices).
Removing the pendant vertices and their incident edges yields a
Hamiltonian path in G that starts at a neighbor of a and ends at another
neighbor of a.  Adding the two edges incident to a closes the path into
the required Hamiltonian cycle of G.

Conversely, given a Hamiltonian cycle in G, we can start at a neighbor u
of a, traverse the cycle (skipping a), reach the other neighbor v of a,
and prepend p1‑a1‑u and append v‑a2‑p2, obtaining a Hamiltonian path in
G'.

Edge cases: For graphs with n <= 2 the source instance is always a "no"
instance.  We map these to a trivial target instance with n = 0, which is
also a "no" for Hamiltonian Path.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": [[u, v], ...]}`` representing an undirected
        graph for the Hamiltonian Cycle problem.

    Returns
    -------
    dict
        An instance of the Hamiltonian Path problem with the same format.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Source instances with n <= 2 are always NO.  Return a trivial NO
    # instance for the target (n = 0, no edges).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the distinguished vertex a.
    # New vertex mapping:
    #   a1 -> 0
    #   a2 -> 1
    #   p1 -> 2
    #   p2 -> 3
    #   original vertex i (i >= 1) -> i + 3
    new_n = n + 3
    new_edges_set = set()

    def add_edge(u: int, v: int) -> None:
        # store edges with smaller vertex first to avoid duplicates
        if u > v:
            u, v = v, u
        new_edges_set.add((u, v))

    # Add pendant edges
    add_edge(2, 0)  # p1 - a1
    add_edge(3, 1)  # p2 - a2

    for u, v in edges:
        if u == 0 or v == 0:
            # Edge incident to the distinguished vertex a.
            other = v if u == 0 else u
            new_idx = other + 3  # shift original index
            # Connect both a1 and a2 to this neighbor.
            add_edge(0, new_idx)  # a1 - neighbor
            add_edge(1, new_idx)  # a2 - neighbor
        else:
            # Edge between two non‑a vertices; just shift both indices.
            add_edge(u + 3, v + 3)

    # Convert set to required list format.
    new_edges = [[u, v] for (u, v) in sorted(new_edges_set)]
    return {"n": new_n, "edges": new_edges}

