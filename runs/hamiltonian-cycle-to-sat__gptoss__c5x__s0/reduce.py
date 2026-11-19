"""Reduction from Hamiltonian Cycle (undirected) to SAT (CNF).

The reduction follows the classic encoding using a permutation matrix.
For a graph G with n vertices we create n² Boolean variables
    x_{i,v}  (0 ≤ i < n, 0 ≤ v < n)
meaning "vertex v is placed at position i in the Hamiltonian cycle".

Constraints encoded as CNF clauses:
1. Each position i is occupied by exactly one vertex.
2. Each vertex appears in exactly one position.
3. Consecutive positions must correspond to an edge of G (non‑edges are
   forbidden).

If n ≤ 2 the source instance is always a NO‑instance, so we output a SAT
instance containing a single empty clause, which is unsatisfiable.

The produced SAT instance uses variables numbered from 1 to n*n in the
order ``var_id = i * n + v + 1``.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Set

from problems import HamiltonianCycle, Sat, InvalidInstance


def _var_id(i: int, v: int, n: int) -> int:
    """Map the pair (position i, vertex v) to a SAT variable id (1‑based)."""
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to an equivalent SAT instance.

    The returned instance is a dict ``{"num_vars": m, "clauses": [...]}``
    that satisfies the format required by :class:`Sat`.
    """
    # Validate source instance first.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: n <= 2 -> always NO. Produce unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}  # an empty clause is unsat

    # Build adjacency set for quick lookup.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []
    m = n * n  # total number of variables

    # 1. Exactly one vertex per position.
    for i in range(n):
        # At least one vertex in position i.
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)
        # At most one: pairwise exclusion.
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 2. Each vertex appears exactly once.
    for v in range(n):
        # At least once.
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)
        # At most once: pairwise exclusion.
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 3. Edge constraints: forbid consecutive positions that are not edges.
    # For each non‑edge {u, v} and each position i, add clauses preventing
    # (i,u) followed by (i+1,v) and the symmetric direction.
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if (u, v) in adj:
                continue  # allowed edge, no clause needed
            # non‑edge, forbid adjacency in both directions.
            for i in range(n):
                nxt = (i + 1) % n
                clauses.append([-_var_id(i, u, n), -_var_id(nxt, v, n)])
                clauses.append([-_var_id(i, v, n), -_var_id(nxt, u, n)])

    # Validate the produced SAT instance before returning.
    Sat.validate({"num_vars": m, "clauses": clauses})
    return {"num_vars": m, "clauses": clauses}

