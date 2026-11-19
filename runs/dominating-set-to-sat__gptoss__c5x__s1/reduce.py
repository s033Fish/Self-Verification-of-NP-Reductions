"""Reduction from Dominating Set to SAT.

The source problem is :class:`DominatingSet` and the target is :class:`Sat`.

We encode a dominating set of size at most k using Boolean variables
``y_{i,j}`` meaning *vertex i occupies position j* (0 ≤ i < n, 0 ≤ j < k).
A dummy vertex with index n represents an unused slot; it never helps
dominate any vertex.

Constraints:
1. Each position j must be occupied by exactly one vertex (real or dummy).
   – a clause with all possible occupants ensures at least one.
   – pairwise negative clauses forbid two occupants.
2. A real vertex cannot appear in two different positions (at‑most‑once).
3. Domination: for every vertex v, at least one selected vertex lies in its
   closed neighbourhood N[v].

Edge cases follow the specification of DominatingSet.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import DominatingSet, Sat, InvalidInstance


def _var_index(i: int, j: int, k: int) -> int:
    """Return a SAT variable number for vertex i (or dummy) at position j.

    Variables are 1‑based as required by the SAT format.
    """
    return i * k + j + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a DominatingSet instance to an equivalent SAT instance.

    Returns a dict ``{"num_vars": m, "clauses": [...]}`` suitable for
    ``Sat.validate``.
    """
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Trivial cases
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}  # unsat
    if n == 0:
        return {"num_vars": 0, "clauses": []}   # trivially sat
    if k >= n:
        return {"num_vars": 0, "clauses": []}   # can take all vertices

    # Build closed neighbourhoods
    neigh: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)
    for i in range(n):
        neigh[i].add(i)

    clauses: List[List[int]] = []
    # include dummy vertex => n+1 vertices total
    num_vars = (n + 1) * k

    # 1. Each position must be occupied by exactly one vertex (real or dummy)
    for j in range(k):
        occupants = [_var_index(i, j, k) for i in range(n + 1)]
        # at least one
        clauses.append(occupants)
        # at most one (pairwise)
        for a in range(len(occupants)):
            for b in range(a + 1, len(occupants)):
                clauses.append([-occupants[a], -occupants[b]])

    # 2. A real vertex cannot appear in two different positions
    for i in range(n):
        for j in range(k):
            for l in range(j + 1, k):
                clauses.append([-_var_index(i, j, k), -_var_index(i, l, k)])

    # 3. Domination clauses
    for v in range(n):
        clause: List[int] = []
        for i in neigh[v]:
            for j in range(k):
                clause.append(_var_index(i, j, k))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

