"""Reduction from Dominating Set to SAT.

The source problem is DominatingSet and the target is Sat.  This module
provides a function ``reduce`` that maps an instance of Dominating Set to an
instance of SAT such that the SAT instance is satisfiable iff the original
graph has a dominating set of size at most ``k``.

The construction uses a variable ``x_v`` for each vertex ``v`` (1‑based
indices in the SAT encoding) and adds a clause guaranteeing that each vertex
is dominated.  To enforce the cardinality bound ``|D| ≤ k`` we employ the
sequential‑counter encoding (Sinz, 2005).  The reduction handles all edge
cases required by the specification.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import DominatingSet, Sat


def _unsat_instance() -> Dict[str, Any]:
    """Return a trivially unsatisfiable SAT instance (contains an empty clause)."""
    return {"num_vars": 1, "clauses": [[]]}


def _trivially_sat_instance(num_vars: int = 0) -> Dict[str, Any]:
    """Return a trivially satisfiable SAT instance (no clauses)."""
    return {"num_vars": num_vars, "clauses": []}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to an equivalent SAT instance.

    The returned SAT instance is satisfiable iff the original graph has a
    dominating set of size at most ``k``.
    """
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ----------------------------------------------------
    if k < 0:
        return _unsat_instance()
    if n == 0:
        # Empty graph – always has a dominating set (the empty set).
        return _trivially_sat_instance()
    if k == 0:
        # Non‑empty graph cannot be dominated by 0 vertices.
        return _unsat_instance()
    if k >= n:
        # Cardinality constraint is redundant – only need domination clauses.
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        clauses: List[List[int]] = []
        for v in range(n):
            clause = [v + 1]
            clause.extend([nbr + 1 for nbr in adj[v]])
            clauses.append(clause)
        return {"num_vars": n, "clauses": clauses}

    # General case (0 < k < n) -------------------------------------------
    # Build adjacency list.
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Helper to map (i, j) -> auxiliary variable for the sequential counter.
    def s_var(i: int, j: int) -> int:
        # Variables 1..n are the x_v variables.
        # Auxiliary variables start at n+1.
        return n + (i - 1) * k + j

    total_vars = n + n * k
    clauses: List[List[int]] = []

    # 1. Domination clauses: each vertex must be dominated.
    for v in range(n):
        clause = [v + 1]
        clause.extend([nbr + 1 for nbr in adj[v]])
        clauses.append(clause)

    # 2. Sequential counter encoding for at‑most‑k true x‑variables.
    # First vertex (i = 1): s_1,1 ↔ x1
    clauses.append([-1, s_var(1, 1)])
    clauses.append([-s_var(1, 1), 1])

    for i in range(2, n + 1):
        xi = i
        # (¬xi ∨ s_i,1)
        clauses.append([-xi, s_var(i, 1)])
        # (¬s_{i-1,1} ∨ s_{i,1})
        clauses.append([-s_var(i - 1, 1), s_var(i, 1)])
        # (¬xi ∨ ¬s_{i-1,k})
        clauses.append([-xi, -s_var(i - 1, k)])
        for j in range(2, k + 1):
            # (¬xi ∨ ¬s_{i-1,j-1} ∨ s_{i,j})
            clauses.append([-xi, -s_var(i - 1, j - 1), s_var(i, j)])
            # (¬s_{i-1,j} ∨ s_{i,j})
            clauses.append([-s_var(i - 1, j), s_var(i, j)])

    return {"num_vars": total_vars, "clauses": clauses}

