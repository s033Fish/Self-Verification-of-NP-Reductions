"""Reduction from Hamiltonian Path to SAT.

Given an undirected graph G = (V, E) with |V| = n, we create a CNF formula
that is satisfiable iff G has a Hamiltonian path (any endpoints).

Variables:
    x_{i,v}  (1 <= i <= n, 0 <= v < n)  – vertex v appears at position i.
    We number variables from 1 to n*n using the mapping:
        var(i, v) = i * n + v + 1   where i is 0‑based position.

Clauses encode:
  1. Each position i contains at least one vertex.
  2. No position contains two different vertices.
  3. Each vertex appears in at least one position.
  4. No vertex appears in two different positions.
  5. Consecutive positions must be connected by an edge.

Edge cases:
  * n = 0 → unsatisfiable (return a formula with an empty clause).
  * n = 1 → trivially satisfiable (return an empty formula).
"""

from typing import Dict, List, Any, Set, Tuple


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge cases
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Vacuously satisfiable: no clauses.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency set for quick lookup of edges.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue
        adj.add((u, v))
        adj.add((v, u))

    def var(pos: int, vertex: int) -> int:
        """Return SAT variable number for vertex at position.
        pos is 0‑based (0 .. n-1), vertex is 0‑based (0 .. n-1).
        """
        return pos * n + vertex + 1

    clauses: List[List[int]] = []

    # 1. Each position has at least one vertex.
    for i in range(n):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two different vertices (pairwise at most one).
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [var(i, v) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # 5. Edge constraints for consecutive positions.
    # For each pair of non‑adjacent vertices (including same vertex), forbid them consecutively.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if (u, v) not in adj:
                    # not an edge, cannot be consecutive
                    clauses.append([-var(i, u), -var(i + 1, v)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}


# The module exposes only the reduce function as required.
__all__ = ["reduce"]
