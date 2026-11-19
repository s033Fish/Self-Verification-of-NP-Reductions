"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The source problem instance has the form:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1 and edges are undirected.

The target SAT instance must be a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are integers: +v for true, -v for false, with variables 1..m.

We use the classic polynomial‑time reduction that introduces a Boolean
variable x_{i,v} meaning "vertex v occupies position i in the Hamiltonian
path".  Positions are 0..n-1, so we need n·n variables.  The reduction
adds clauses that enforce:

1. Every position is occupied by **at least one** vertex.
2. No position is occupied by **more than one** vertex.
3. Every vertex appears in **at least one** position.
4. No vertex appears in **more than one** position.
5. Non‑adjacent vertices cannot appear consecutively in the path.

Edge cases:
* n = 0 – the Hamiltonian‑Path instance is a definite NO.  We return a SAT
  formula containing an empty clause, which is unsatisfiable.
* n = 1 – always YES.  We return a trivially satisfiable formula (no
  clauses) with a single variable.

The construction runs in O(n³) time and produces O(n³) clauses, which is
polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

def _var_index(i: int, v: int, n: int) -> int:
    """Map a position *i* and vertex *v* to a SAT variable number (1‑based).

    Variables are numbered consecutively: first all vertices for position 0,
    then for position 1, and so on.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    The returned SAT instance is satisfiable iff the input graph contains a
    Hamiltonian path (undirected, endpoints unrestricted).
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: n == 0 – always NO.
    if n == 0:
        # An empty clause makes the formula unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # Edge case: n == 1 – always YES.
    if n == 1:
        # A formula with no clauses is trivially satisfiable.
        return {"num_vars": 1, "clauses": []}

    # Build a set for quick adjacency checks. Store both directions.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position i contains two different vertices (pairwise mutual exclusion).
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 3. Each vertex v appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 5. Non‑edges cannot be consecutive in the path.
    # For every pair of distinct vertices (u, v) that are NOT adjacent,
    # forbid them from occupying consecutive positions i and i+1.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if (u, v) not in adj:
                    # (-x_{i,u} ∨ -x_{i+1,v})
                    clauses.append([-_var_index(i, u, n), -_var_index(i + 1, v, n)])

    return {"num_vars": n * n, "clauses": clauses}

