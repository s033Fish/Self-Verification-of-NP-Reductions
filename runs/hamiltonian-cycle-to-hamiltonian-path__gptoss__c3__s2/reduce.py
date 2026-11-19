"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem is HamiltonianCycle (undirected cycle) and the target
problem is HamiltonianPath (undirected path with arbitrary endpoints).  Both
use the same graph representation: a dict with keys "n" and "edges" where edges
are undirected pairs [u, v].

Standard reduction: pick a vertex (0) and split it into two copies.  To force a
Hamiltonian path to start at one copy and end at the other we attach two pendant
vertices s and t to the copies.  Any Hamiltonian cycle in the original graph
can be broken at vertex 0, yielding a Hamiltonian path from the first copy to
the second; the pendant vertices then extend this to a Hamiltonian path from s
to t in the new graph.  Conversely, any Hamiltonian path from s to t must use
the two pendant edges, and after removing s, t and merging the copies we obtain
a Hamiltonian cycle in the original graph.

Edge cases: for n <= 2 the source instance is always NO, so we map it to a
trivially NO target instance (n=0, no edges).
"""

from __future__ import annotations
from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Source always NO for n <= 2; map to a NO target.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Indices for new vertices.
    copy0 = 0                     # original vertex 0 stays as is
    copy0b = n                    # new copy of vertex 0
    pendant_s = n + 1             # pendant attached to copy0
    pendant_t = n + 2             # pendant attached to copy0b
    new_n = n + 3                 # total vertices after addition

    new_edges_set = set()

    for u, v in edges:
        if u == 0 or v == 0:
            other = v if u == 0 else u
            # connect both copies to the neighbour
            a, b = (copy0, other) if copy0 < other else (other, copy0)
            new_edges_set.add((a, b))
            a, b = (copy0b, other) if copy0b < other else (other, copy0b)
            new_edges_set.add((a, b))
        else:
            a, b = (u, v) if u < v else (v, u)
            new_edges_set.add((a, b))

    # pendant edges
    new_edges_set.add((pendant_s, copy0))
    new_edges_set.add((pendant_t, copy0b))

    new_edges = [[u, v] for (u, v) in new_edges_set]
    return {"n": new_n, "edges": new_edges}

