"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

Given an undirected graph G = (V, E) we construct a graph G' as follows:

1. If |V| <= 2 or E is empty, return a trivially "no" instance.
2. Choose an arbitrary edge (u, v) ∈ E.
3. Remove the edge (u, v) from the edge set.
4. Introduce two new vertices s and t.
5. Add edges (s, u) and (t, v).

The resulting graph G' has |V|+2 vertices.  Vertices s and t have degree 1, so any
Hamiltonian *path* in G' must start at s and end at t.  Removing s, t and the
edges incident to them yields a Hamiltonian *path* from u to v in G\{(u,v)}.
Adding back the removed edge (u, v) closes this path into a Hamiltonian *cycle*
in G.  Conversely, a Hamiltonian cycle in G contains the edge (u, v); deleting
it gives a Hamiltonian u‑v path, which extends to a Hamiltonian path in G'
by the new edges.

Thus G has a Hamiltonian cycle iff G' has a Hamiltonian path.  The construction
runs in linear time.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import HamiltonianCycle, HamiltonianPath


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance:
        A dict representing a HamiltonianCycle instance.

    Returns
    -------
    dict
        An equivalent HamiltonianPath instance.
    """
    # Validate the source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = list(instance["edges"])  # copy

    # Trivial no‑instances for small n.
    if n <= 2:
        return {"n": 0, "edges": []}
    if not edges:
        return {"n": 0, "edges": []}

    # Choose an arbitrary edge (u, v).
    u, v = edges[0]

    # New vertices s and t.
    s = n
    t = n + 1
    new_n = n + 2

    # Build edge list without the chosen edge.
    new_edges: List[List[int]] = []
    for a, b in edges:
        if (a == u and b == v) or (a == v and b == u):
            continue  # skip the chosen edge
        new_edges.append([a, b])
    # Add connections for s and t.
    new_edges.append([s, u])
    new_edges.append([t, v])

    reduced_instance = {"n": new_n, "edges": new_edges}
    HamiltonianPath.validate(reduced_instance)
    return reduced_instance

