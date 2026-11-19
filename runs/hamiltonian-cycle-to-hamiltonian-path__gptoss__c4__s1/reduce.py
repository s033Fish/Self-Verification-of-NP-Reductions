"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

Classic reduction:
- Choose a vertex v (we use the last vertex n-1 when n>0).
- Replace v by two vertices v_in and v_out.
- For each edge (v, u) in the original graph, add edges (v_in, u) and (v_out, u).
- Add edge (v_in, v_out).
- Add two pendant vertices s and t attached to v_in and v_out respectively.

Any Hamiltonian cycle in the original graph corresponds to a Hamiltonian path
starting at s and ending at t in the constructed graph, and vice‑versa.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianCycle, HamiltonianPath


def reduce(instance: Dict) -> Dict:
    """Reduce Hamiltonian Cycle to Hamiltonian Path.

    Parameters
    ----------
    instance: dict
        Valid HamiltonianCycle instance.

    Returns
    -------
    dict
        Valid HamiltonianPath instance equivalent to the source.
    """
    # Validate source instance
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # For n <= 2 the source is always NO; return a known NO instance for path.
    if n <= 2:
        no_instance = {"n": 0, "edges": []}
        HamiltonianPath.validate(no_instance)
        return no_instance

    # Choose the last vertex as the one to split.
    split = n - 1
    # New vertex indices:
    v_in = n - 1      # replaces split
    v_out = n         # new vertex
    s = n + 1         # pendant start
    t = n + 2         # pendant end
    new_n = n + 3

    new_edges: List[List[int]] = []
    for u, v in edges:
        if split not in (u, v):
            # edge between untouched vertices stays the same
            new_edges.append([u, v])
        else:
            # edge incident to the split vertex
            other = v if u == split else u
            # connect both copies to the other vertex
            new_edges.append([v_in, other])
            new_edges.append([v_out, other])
    # edge between the two copies of the split vertex
    new_edges.append([v_in, v_out])
    # pendant edges
    new_edges.append([s, v_in])
    new_edges.append([t, v_out])

    reduced_instance = {"n": new_n, "edges": new_edges}
    HamiltonianPath.validate(reduced_instance)
    return reduced_instance

