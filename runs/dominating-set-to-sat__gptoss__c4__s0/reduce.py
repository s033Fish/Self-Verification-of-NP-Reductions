"""Reduction from Dominating Set to SAT.

We map a Dominating‑Set instance (graph G with n vertices and integer k) to a
CNF formula that is satisfiable iff G has a dominating set of size at most k.
The construction uses selector variables y_{i,v} meaning *in position i (1‑based) we
choose vertex v*.  Positions allow duplicates, so using at most k vertices is
captured by exactly k positions (some may be unused by picking any vertex).  The
formula enforces:

1. Every position chooses **at least one** vertex.
2. Every position chooses **at most one** vertex (pairwise mutual exclusion).
3. Every graph vertex v is dominated by **some** chosen vertex in *any* position –
   i.e. the clause (∨_{i=1..k} ∨_{u∈N[v]} y_{i,u}) where N[v] are v and its
   neighbours.

Edge cases:
* k < 0 – unsatisfiable (empty clause).
* n = 0 – trivially satisfiable (no variables, no clauses).
* k = 0 and n > 0 – unsatisfiable because no vertex can be selected to dominate
  the graph.

The reduction runs in O(k·n + n·deg) time and produces O(k·n + n·k) clauses, i.e.
polynomial in the input size.
"""

from __future__ import annotations

from typing import Dict, List

from problems import DominatingSet, Sat


def _y_var(i: int, v: int, n: int) -> int:
    """Map position i (1‑based) and vertex v (0‑based) to a SAT variable.
    Variables are numbered from 1 upward.
    """
    # we allocate n variables per position; offset by (i‑1)*n
    return (i - 1) * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce Dominating‑Set to SAT.

    Returns a dict with keys "num_vars" and "clauses" as required by the SAT
    problem definition.
    """
    DominatingSet.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}  # unsat
    if n == 0:
        return {"num_vars": 0, "clauses": []}   # sat
    if k == 0:
        # No positions to select vertices, but graph non‑empty → unsat
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency list including self (closed neighbourhood)
    adj: List[set[int]] = [set([v]) for v in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses: List[List[int]] = []
    # 1. At least one vertex per position i
    for i in range(1, k + 1):
        clause = [_y_var(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position i (pairwise)
    for i in range(1, k + 1):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_y_var(i, v, n), -_y_var(i, w, n)])

    # 3. Dominating constraints: each vertex must be dominated by some chosen vertex
    for v in range(n):
        clause: List[int] = []
        for i in range(1, k + 1):
            for u in adj[v]:
                clause.append(_y_var(i, u, n))
        # clause is non‑empty because n>0 and k>0
        clauses.append(clause)

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

