"""Reduction from Clique to SAT.

The source problem is defined in ``problems.Clique`` and the target in
``problems.Sat``.  An instance of Clique is a dictionary with keys
``"n"``, ``"edges"`` and ``"k"``.  An instance of SAT is a dictionary with
keys ``"num_vars"`` and ``"clauses"`` where each clause is a list of integer
literals (positive for true, negative for false).

The classic polynomial‑time reduction introduces a Boolean variable
``x_{i,p}`` meaning *vertex i occupies position p in the alleged clique*.
Positions are numbered ``0 .. k-1``.  The reduction creates the following
constraints as CNF clauses:

1. **Each position is occupied** – for every position ``p`` we add a clause
   ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p})``.
2. **At most one vertex per position** – for every position ``p`` and every
   distinct pair of vertices ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.
3. **A vertex cannot occupy two positions** – for every vertex ``i`` and
   distinct positions ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.
4. **Non‑edges are forbidden** – for every unordered non‑edge ``{i, j}``
   (i.e., ``i != j`` and the edge is not present) and for every pair of
   positions ``p != q`` we add ``(¬x_{i,p} ∨ ¬x_{j,q})``.  This enforces that
   any two selected vertices are adjacent.

The variable numbering follows the SAT specification (variables are
1‑based).  We map ``x_{i,p}`` to the integer ``i * k + p + 1``.

Edge‑case handling:
* If ``k <= 0`` the Clique instance is always a *yes* instance.  We return
  a trivially satisfiable SAT formula – zero variables and no clauses.
* The generic construction works for all other cases, including ``k > n``
  (which yields an unsatisfiable formula) and ``n == 0``.

The function validates the input using ``Clique.validate`` before
performing the reduction.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the Clique format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k <= 0 is always yes – return a trivially satisfiable formula.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # Build adjacency set for quick look‑ups.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # Helper to map (i, p) -> variable number (1‑based).
    def var(i: int, p: int) -> int:
        return i * k + p + 1

    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [var(i, p) for i in range(n)]
        # If n == 0 the clause will be empty, which correctly makes the
        # formula unsatisfiable (matching the Clique answer for n == 0).
        clauses.append(clause)

    # 2. At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, p), -var(j, p)])

    # 3. A vertex cannot appear in two different positions.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-var(i, p), -var(i, q)])

    # 4. Non‑edges are forbidden between any two selected vertices.
    #    For each unordered pair (i, j) that is NOT an edge, add clauses
    #    preventing them from occupying distinct positions.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                for p in range(k):
                    for q in range(k):
                        if p != q:
                            clauses.append([-var(i, p), -var(j, q)])

    num_vars = n * k
    return {"num_vars": num_vars, "clauses": clauses}

