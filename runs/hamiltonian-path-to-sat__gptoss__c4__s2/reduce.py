"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`HamiltonianPath` defined in ``problems.py``.
The target problem is :class:`Sat` (CNF satisfiability).

For a graph G = (V, E) with |V| = n we create a CNF formula that is
satisfiable iff G contains a Hamiltonian path (undirected, any endpoints).

Encoding (standard textbook reduction):

* Variables ``x_{i,v}`` (position i contains vertex v) for i, v in 0..n-1.
  They are numbered from 1 to n*n in row‑major order:
  ``var(i, v) = i * n + v + 1``.

* **Exactly‑one‑vertex‑per‑position** – for each position i we add a clause
  asserting that at least one vertex occupies it and pairwise clauses
  forbidding two different vertices at the same position.

* **Exactly‑one‑position‑per‑vertex** – for each vertex v we add a clause that
  it appears somewhere and pairwise clauses forbidding it to appear in two
  positions.

* **Adjacency constraints** – for each consecutive pair of positions i,i+1
  and for each unordered non‑edge {u, v} we add two clauses:
  ``(~x_{i,u} ∨ ~x_{i+1,v})`` and ``(~x_{i,v} ∨ ~x_{i+1,u})``.
  This guarantees that consecutive vertices in the path must be adjacent.

Edge cases are handled explicitly so that the reduction runs in polynomial
time for all inputs:

* ``n = 0`` – Hamiltonian Path is always *no*.  We return a formula containing
  a single empty clause ``[]`` which is unsatisfiable.
* ``n = 1`` – always *yes*.  We return a trivially satisfiable formula with
  zero variables and zero clauses.
* ``n = 2`` – the generic encoding already works, but we keep the same logic.

The function ``reduce(instance)`` validates the input using the provided
``HamiltonianPath.validate`` method and returns a dictionary adhering to the
SAT instance format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, Sat


def _var(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` to a SAT variable index (1‑based)."""
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as defined for the
        :class:`HamiltonianPath` problem.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable exactly when the input graph has a Hamiltonian path.
    """
    # Validate source instance – will raise InvalidInstance on malformed input.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case handling
    if n == 0:
        # No vertices → answer is NO. Return an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable – zero variables, no clauses.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    clauses: List[List[int]] = []
    m = n * n  # total variables

    # 1. At least one vertex at each position i.
    for i in range(n):
        clause = [_var(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position i (pairwise mutual exclusion).
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears at most once (pairwise).
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # 5. Adjacency constraints for consecutive positions.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if not adj[u][v]:
                    # forbid u at i and v at i+1
                    clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])
        # The loop above already handles both orders because we iterate over all (u,v).
        # No need for a separate symmetric clause.

    return {"num_vars": m, "clauses": clauses}

