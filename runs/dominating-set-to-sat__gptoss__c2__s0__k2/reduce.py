"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1.

The target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are signed integers: +v for variable v being true, -v for false.

We construct a CNF formula that is satisfiable iff the graph has a
dominating set of size at most k.

Encoding:
    For each vertex i (0 <= i < n) and each rank r (1 <= r <= k) we create a
    boolean variable s_{i,r} meaning "vertex i is selected and assigned rank r".
    The rank acts as a unique identifier, ensuring that no more than k vertices
    are selected: each rank can be used by at most one vertex, and a vertex can
    use at most one rank.

    * At‑most‑one‑rank-per-vertex:
        for each i and for each pair r1 < r2:
            (¬s_{i,r1} ∨ ¬s_{i,r2})
    * At‑most‑one‑vertex-per-rank:
        for each r and for each pair i1 < i2:
            (¬s_{i1,r} ∨ ¬s_{i2,r})
    * Domination constraints:
        for each vertex v, the clause requires that either v itself is selected
        (any rank) or one of its neighbours is selected (any rank):
            (s_{v,1} ∨ … ∨ s_{v,k} ∨ s_{u1,1} ∨ … ∨ s_{u1,k} ∨ … )
        where u1, u2, … are the neighbours of v.

Edge‑case handling:
    * k < 0 – always unsatisfiable. We return a formula containing an empty
      clause.
    * n == 0 – the empty graph is dominated by the empty set, which is allowed
      for any k >= 0. Return a trivially satisfiable formula (no clauses).
    * k >= n – any set of vertices works, so we again return a trivially
      satisfiable formula.
    * k == 0 with n > 0 – impossible to dominate a non‑empty graph, return an
      unsatisfiable formula.

The reduction runs in polynomial time (O(n^2 * k + n * k * deg)).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if n == 0:
        # Vacuously satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Always possible – return empty formula.
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # Non‑empty graph cannot be dominated by 0 vertices.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency list.
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Mapping (vertex, rank) -> variable number (1‑based).
    def var(i: int, r: int) -> int:
        return i * k + r  # r in 1..k, i in 0..n-1

    clauses: List[List[int]] = []

    # 1) At‑most‑one‑rank‑per‑vertex.
    for i in range(n):
        for r1 in range(1, k):
            for r2 in range(r1 + 1, k + 1):
                clauses.append([-var(i, r1), -var(i, r2)])

    # 2) At‑most‑one‑vertex‑per‑rank.
    for r in range(1, k + 1):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                clauses.append([-var(i1, r), -var(i2, r)])

    # 3) Domination clauses.
    for v in range(n):
        literals: List[int] = []
        # v itself can dominate.
        for r in range(1, k + 1):
            literals.append(var(v, r))
        # any neighbor can dominate.
        for u in adj[v]:
            for r in range(1, k + 1):
                literals.append(var(u, r))
        # The clause must be non‑empty (k > 0 ensures this).
        clauses.append(literals)

    num_vars = n * k
    return {"num_vars": num_vars, "clauses": clauses}

