"""Reduction from Vertex Cover to SAT.

We encode the existence of a vertex cover of size at most ``k`` using boolean
variables ``y_{i,j}`` where ``i`` is a vertex (0‑based) and ``j`` is a position
``1..k``.  Variable ``y_{i,j}`` is true iff vertex *i* is chosen for position *j*
in the cover.

The CNF consists of:

1. **Exactly‑one‑per‑position clauses** – for each position ``j`` we add a
   clause asserting that *some* vertex occupies the position and pairwise
   negative clauses forbidding two different vertices from occupying the same
   position.  This forces each position to be assigned a *single* vertex.
2. **Edge clauses** – for each edge ``(u,v)`` we add a clause containing all
   literals ``y_{u,1},…,y_{u,k}, y_{v,1},…,y_{v,k}``.  At least one endpoint must be
   selected in some position.

Repeating the same vertex in several positions does not increase the number
of *distinct* vertices used, so the total number of distinct vertices is at most
``k``.  The formula has ``O(n·k + |E|·k)`` clauses – polynomial in the input
size.

Edge cases are treated explicitly to keep the output tiny.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_index(i: int, j: int, k: int) -> int:
    """Map vertex ``i`` (0‑based) and position ``j`` (1‑based) to a SAT variable.

    Variables are numbered from 1 to ``n * k``.
    """
    return i * k + j


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SAT instance.

    The returned SAT instance is satisfiable iff the input graph has a vertex
    cover of size at most ``k``.
    """
    VertexCover.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases ----------------------------------------------------------
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}
    if not edges:
        return {"num_vars": 1, "clauses": []}
    if k == 0:
        return {"num_vars": 1, "clauses": [[]]}

    # Focus only on vertices that appear in edges.
    vertex_set = {v for e in edges for v in e}
    n_prime = len(vertex_set)
    if k >= n_prime:
        return {"num_vars": 1, "clauses": []}
    mapping = {v: i for i, v in enumerate(sorted(vertex_set))}
    remapped_edges = [[mapping[u], mapping[v]] for u, v in edges]

    # General case --------------------------------------------------------
    num_vars = n_prime * k
    clauses: List[List[int]] = []

    # 1. Exactly‑one‑per‑position clauses.
    for j in range(1, k + 1):
        # At least one vertex in position j.
        clause = [_var_index(i, j, k) for i in range(n_prime)]
        clauses.append(clause)
        # At most one vertex in position j (pairwise negative).
        for i1 in range(n_prime):
            for i2 in range(i1 + 1, n_prime):
                clauses.append([-_var_index(i1, j, k), -_var_index(i2, j, k)])

    # 2. Edge clauses.
    for u, v in remapped_edges:
        clause = [_var_index(u, j, k) for j in range(1, k + 1)] + [_var_index(v, j, k) for j in range(1, k + 1)]
        clauses.append(clause)

    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

