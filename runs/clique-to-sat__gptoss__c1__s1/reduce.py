"""Reduction from Clique to SAT.

Given an instance of the Clique problem, produce an equivalent SAT instance
in conjunctive normal form.  The reduction follows the classic encoding
using variables x_{i,v} meaning "vertex v occupies position i in the
clique" (positions are 0-indexed up to k-1).  The resulting formula is
satisfiable iff the original graph contains a clique of size at least k.

Edge cases are handled explicitly:
  * k <= 0  – always yes, we output an empty formula (no clauses).
  * k > n  – always no, we output a formula containing an empty clause
    which is unsatisfiable.
"""
from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Trivial cases
    if k <= 0:
        # Empty formula is always satisfiable
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula – contain an empty clause
        return {"num_vars": 0, "clauses": [[]]}

    # Helper to map (position, vertex) to a 1‑based variable index
    def var_id(pos: int, vertex: int) -> int:
        # pos in [0, k-1], vertex in [0, n-1]
        return pos * n + vertex + 1

    # Build adjacency set for O(1) edge lookup
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    clauses: List[List[int]] = []

    # 1. At least one vertex in each position
    for i in range(k):
        clause = [var_id(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position (pairwise mutual exclusion)
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var_id(i, u), -var_id(i, v)])

    # 3. A vertex appears in at most one position
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var_id(i, v), -var_id(j, v)])

    # 4. Non‑edges cannot both be selected (for any two distinct positions)
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v:
                        continue
                    if not adj[u][v]:
                        clauses.append([-var_id(i, u), -var_id(j, v)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}


# The module exposes only the reduce function as required by the task.
__all__ = ["reduce"]

