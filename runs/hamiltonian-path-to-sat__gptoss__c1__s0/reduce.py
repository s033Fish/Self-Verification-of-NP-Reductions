"""Reduction from Hamiltonian Path (undirected) to SAT.

The source problem instance is a dict with keys:
    "n": number of vertices (0‑based, vertices are 0..n‑1)
    "edges": list of undirected edges, each as [u, v] with u != v.

The target SAT instance follows the format used in ``problems.py``:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where literals are signed integers (+v for true, -v for false) and
variables are numbered from 1 to m.

The reduction creates a variable x_{i,v} (encoded as a single integer
identifier) meaning *vertex v occupies position i* in a Hamiltonian path.
For a graph with n vertices we therefore use n·n variables.

Constraints encoded as CNF clauses:
  1. Every position i (0 ≤ i < n) contains *some* vertex.
  2. No position contains two different vertices (pairwise mutual exclusion).
  3. Every vertex appears in *some* position.
  4. No vertex appears in two different positions.
  5. Consecutive positions must correspond to an edge of the graph.

Edge cases:
  * n = 0 → the answer is always NO. We output an unsatisfiable formula
    (a single empty clause).
  * n = 1 → the answer is always YES. An empty clause list (trivially
    satisfiable) suffices.
  * n = 2 follows automatically from the generic construction, but the
    reduction also works for this case.

The function runs in polynomial time (Θ(n³) clauses in the worst case).
"""

from __future__ import annotations

from typing import Dict, List

def _var_id(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1..n*n in row‑major order:
    id = i * n + v + 1.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": [[u, v], ...]}``

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}``
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge‑case handling ---------------------------------------------------
    if n == 0:
        # No vertices → always NO. Return an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Single vertex → always YES. Empty clause list is satisfiable.
        return {"num_vars": 1, "clauses": []}

    # Build adjacency lookup for quick edge tests.
    adj = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    m = n * n  # total variables
    clauses: List[List[int]] = []

    # 1. Every position i contains at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two different vertices.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([ -_var_id(i, v, n), -_var_id(i, w, n) ])

    # 3. Every vertex appears in at least one position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([ -_var_id(i, v, n), -_var_id(j, v, n) ])

    # 5. Consecutive positions must correspond to an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if (u, v) not in adj:
                    # forbid u at position i and v at position i+1
                    clauses.append([ -_var_id(i, u, n), -_var_id(i + 1, v, n) ])

    return {"num_vars": m, "clauses": clauses}

