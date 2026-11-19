"""Reduction from Vertex Cover to SAT.

Given a graph G = (V, E) with |V| = n and an integer k, we construct a
CNF formula that is satisfiable iff G has a vertex cover of size at most k.
The construction uses the standard “position” encoding:
- For each position i = 1..k and each vertex v ∈ V we introduce a Boolean
  variable X_{i,v} which is true exactly when vertex v occupies position i
  in the chosen cover.
- The formula enforces that each position is occupied by exactly one vertex,
  that no vertex occupies two different positions, and that every edge has
  at least one endpoint selected in some position.

The formula is always polynomial in the size of the input.
Edge cases are handled explicitly:
* k < 0 → unsatisfiable (empty clause).
* k ≥ n → trivially satisfiable (no clauses).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 -> unsatisfiable formula (contains empty clause)
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}

    # Edge case: k >= n -> always satisfiable, return empty formula
    if k >= n:
        return {"num_vars": 1, "clauses": []}

    # Helper to map (position i, vertex v) to a SAT variable number (1‑based)
    def var(i: int, v: int) -> int:
        # i in [0, k-1], v in [0, n-1]
        return i * n + v + 1

    clauses: List[List[int]] = []

    # 1. Each position i must contain at least one vertex
    for i in range(k):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. Each position contains at most one vertex: for each pair v<w
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. No vertex appears in two different positions
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # 4. Every edge must be covered by some selected vertex
    for (u, v) in edges:
        clause = []
        for i in range(k):
            clause.append(var(i, u))
            clause.append(var(i, v))
        clauses.append(clause)

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}


# The module only needs to expose the reduce function.
__all__ = ["reduce"]

