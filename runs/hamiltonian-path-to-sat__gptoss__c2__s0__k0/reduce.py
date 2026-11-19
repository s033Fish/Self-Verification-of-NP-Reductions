"""Reduction from Hamiltonian Path (undirected) to SAT.

The source problem instance is a dictionary with keys:
    - "n": number of vertices (vertices are 0..n-1)
    - "edges": list of undirected edges, each edge is a two‑element list
               [u, v] with u != v.  The edge [u, v] is considered the same as
               [v, u] and will appear at most once.

The target problem is SAT in conjunctive normal form.  An instance is a
dictionary with keys:
    - "num_vars": the number of Boolean variables (named 1..num_vars)
    - "clauses": a list of clauses, each clause is a list of integers where a
                 positive integer +v denotes the literal *v* (variable v is
                 true) and a negative integer -v denotes the literal ¬v.

The reduction creates a variable x_{i,j} (encoded as a single integer) that
means "vertex i appears at position j in the Hamiltonian path".  Positions are
0‑based, i.e. j ∈ {0,…,n‑1}.  The variable identifier is:

    var(i, j) = i * n + j + 1   (so identifiers start at 1)

The SAT formula enforces the usual constraints for Hamiltonian paths:

1. Every position is occupied by *some* vertex.
2. Every vertex appears in *some* position.
3. No vertex appears in two different positions.
4. No two distinct vertices occupy the same position.
5. Non‑adjacent vertices cannot be consecutive in the path.

Edge cases:
* n = 0 – the answer is always NO.  We return a formula with an empty clause,
  which is unsatisfiable.
* n = 1 – the answer is always YES.  The construction below already yields a
  satisfiable formula (a single variable that must be true), but we keep the
  generic construction for simplicity.

The reduction runs in O(n³) time, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        {"n": int, "edges": [[u, v], ...]}

    Returns
    -------
    dict
        {"num_vars": int, "clauses": [[int, ...], ...]}
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case n = 0 : always NO -> unsatisfiable formula (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Helper to map (vertex, position) to a SAT variable id (1‑based).
    def var(i: int, j: int) -> int:
        return i * n + j + 1

    clauses: List[List[int]] = []

    # 1. Every position j must contain at least one vertex.
    for j in range(n):
        clauses.append([var(i, j) for i in range(n)])

    # 2. Every vertex i must appear in at least one position.
    for i in range(n):
        clauses.append([var(i, j) for j in range(n)])

    # 3. No vertex appears in two different positions.
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                clauses.append([-var(i, j), -var(i, k)])

    # 4. No two distinct vertices occupy the same position.
    for j in range(n):
        for i in range(n):
            for k in range(i + 1, n):
                clauses.append([-var(i, j), -var(k, j)])

    # Build a set of existing undirected edges for O(1) look‑ups.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # 5. For each pair of vertices that are NOT connected, forbid them from
    #    being consecutive in either order.
    for i in range(n):
        for k in range(n):
            if i == k:
                continue
            a, b = (i, k) if i < k else (k, i)
            if (a, b) in edge_set:
                continue  # there is an edge, no restriction needed
            # No edge between i and k.
            for j in range(n - 1):
                # i at position j and k at position j+1 cannot both be true.
                clauses.append([-var(i, j), -var(k, j + 1)])
                # k at position j and i at position j+1 cannot both be true.
                clauses.append([-var(k, j), -var(i, j + 1)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

