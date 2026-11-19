"""Reduction from Hamiltonian Path to SAT.

The reduction follows the classic encoding using a variable x_{i,v} that is
true exactly when vertex ``v`` appears at position ``i`` in the Hamiltonian
path.  Positions are numbered 0..n-1 and vertices are also 0..n-1.

Constraints encoded as CNF clauses:

1. **Each position contains exactly one vertex** – a clause with all
   ``x_{i,v}`` for a fixed ``i`` (at least one) and pairwise negative clauses
   ``¬x_{i,u} ∨ ¬x_{i,v}`` for ``u != v`` (at most one).

2. **Each vertex appears exactly once** – analogous clauses over the position
   index.

3. **Consecutive vertices must be adjacent** – for every non‑edge ``{u,v}``
   and every consecutive position pair ``i,i+1`` we add the clause
   ``¬x_{i,u} ∨ ¬x_{i+1,v}`` and its symmetric counterpart.

Edge cases:
* ``n == 0`` – the Hamiltonian‑Path instance is a definite *no*.  We output a
  formula containing an empty clause, which is unsatisfiable.
* ``n >= 1`` – the generic construction works.  For ``n == 1`` the formula has
  a single variable with a unit clause, which is satisfiable.

The function validates the input using the problem class definitions and
produces a dictionary matching the SAT format defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, Sat


def _var(i: int, v: int, n: int) -> int:
    """Return a SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to n*n using the mapping ``i * n + v + 1``.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    The returned SAT instance has the same answer (yes/no) as the input.
    The reduction runs in polynomial time in the size of the graph.
    """
    # Validate source instance
    HamiltonianPath.validate(instance)
    n: int = instance["n"]
    raw_edges: List[List[int]] = instance["edges"]

    # Edge case n == 0 : always unsatisfiable
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}  # empty clause -> UNSAT

    # Build a set of undirected edges for O(1) lookup
    edge_set = {frozenset((u, v)) for u, v in raw_edges}

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex
    for i in range(n):
        clauses.append([_var(i, v, n) for v in range(n)])

    # 2. Each position i has at most one vertex (pairwise mutual exclusion)
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # 3. Each vertex v appears in at least one position
    for v in range(n):
        clauses.append([_var(i, v, n) for i in range(n)])

    # 4. Each vertex v appears at most once
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # 5. Consecutive positions must correspond to an edge in the graph.
    #    For every non‑edge {u, v} we forbid the ordering (u,v) and (v,u).
    non_edges = [
        (u, v)
        for u in range(n)
        for v in range(n)
        if u != v and frozenset((u, v)) not in edge_set
    ]
    for i in range(n - 1):
        for u, v in non_edges:
            clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])
            clauses.append([-_var(i, v, n), -_var(i + 1, u, n)])

    num_vars = n * n
    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced SAT instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

