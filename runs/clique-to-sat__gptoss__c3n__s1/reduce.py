"""Reduction from Clique to SAT.

This module implements a polynomial‑time many‑one reduction from the Clique
problem to Boolean satisfiability (SAT) in conjunctive normal form.  The source
problem definition and validation utilities are provided in ``problems.py``.

The reduction follows the classic textbook construction:

* For each vertex ``i`` (0 ≤ i < n) and each position ``p`` in a potential
  clique (1 ≤ p ≤ k) we create a boolean variable ``x_{i,p}`` that is true iff
  vertex ``i`` occupies position ``p`` in the chosen clique.
* The CNF enforces four families of constraints:
  1. **Every position is occupied** – at least one vertex must be assigned to
     each position.
  2. **At most one vertex per position** – no two distinct vertices share the
     same position.
  3. **A vertex appears at most once** – a vertex cannot occupy two different
     positions.
  4. **Non‑edges cannot both be chosen** – if two vertices are not adjacent,
     they cannot both be part of the clique (regardless of positions).

If ``k <= 0`` the Clique instance is trivially a *yes* instance, so we return a
trivially satisfiable SAT instance (zero variables, no clauses).  If ``k > n``
the instance is always *no*; we return an unsatisfiable formula consisting of a
single empty clause.

The function ``reduce`` validates the source instance, builds the CNF, validates
the resulting SAT instance, and returns it.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat

def _var_index(i: int, p: int, k: int) -> int:
    """Map vertex ``i`` and position ``p`` to a SAT variable number.

    ``i`` is 0‑based, ``p`` is 1‑based (positions are 1..k).  Variables are
    numbered consecutively from 1 to n·k.
    """
    return i * k + p


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned dictionary conforms to the format expected by ``Sat`` and
    satisfies ``Sat.validate``.  It is satisfiable iff the input graph contains a
    clique of size at least ``k``.
    """
    # Validate the source instance using the provided helper.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Handle edge cases directly.
    if k <= 0:
        # Always yes – return a trivially satisfiable formula.
        sat_instance = {"num_vars": 0, "clauses": []}
        Sat.validate(sat_instance)
        return sat_instance
    if k > n:
        # Always no – return an unsatisfiable formula (empty clause).
        sat_instance = {"num_vars": 0, "clauses": [[]]}
        Sat.validate(sat_instance)
        return sat_instance

    # Build adjacency matrix for O(1) edge queries.
    adjacency = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacency[u][v] = adjacency[v][u] = True

    clauses: List[List[int]] = []
    num_vars = n * k

    # 1. Every position must be occupied by at least one vertex.
    for p in range(1, k + 1):
        clause = [_var_index(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. No two vertices share the same position (at most one per position).
    for p in range(1, k + 1):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, p, k), -_var_index(j, p, k)])

    # 3. A vertex cannot appear in two different positions.
    for i in range(n):
        for p in range(1, k + 1):
            for q in range(p + 1, k + 1):
                clauses.append([-_var_index(i, p, k), -_var_index(i, q, k)])

    # 4. Non‑edges cannot both be selected.
    for i in range(n):
        for j in range(i + 1, n):
            if not adjacency[i][j]:
                for p in range(1, k + 1):
                    for q in range(1, k + 1):
                        clauses.append([-_var_index(i, p, k), -_var_index(j, q, k)])

    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

