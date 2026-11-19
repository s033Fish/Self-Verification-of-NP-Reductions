"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The reduction follows the classic encoding of a Hamiltonian cycle as a
CNF formula.  For a graph with ``n`` vertices we introduce a Boolean
variable ``x_{i,v}`` that is true iff vertex ``v`` appears at position ``i``
in the cycle (positions are numbered ``0`` … ``n-1``).  The variable index
used for the SAT instance is ``i * n + v + 1`` – SAT variables are 1‑based.

Constraints encoded as clauses:

1. **Each position contains at least one vertex** – a clause with all
   ``x_{i,*}`` for a fixed ``i``.
2. **No position contains two different vertices** – for every ``i`` and
   distinct ``v,w`` a binary clause ``¬x_{i,v} ∨ ¬x_{i,w}``.
3. **Each vertex appears in exactly one position** – analogous to (1) and
   (2) but swapping the roles of positions and vertices.
4. **Consecutive vertices must be adjacent** – for every non‑edge ``(u,v)``
   and every position ``i`` we add ``¬x_{i,u} ∨ ¬x_{i+1 mod n, v}``.  This
   forbids placing non‑adjacent vertices next to each other in the cycle.

Edge cases:
* For ``n <= 2`` the Hamiltonian‑Cycle problem is defined to be a *no*
  instance.  We therefore return a SAT instance that is unsatisfiable – a
  single empty clause ``[]`` achieves this.

The function validates the input using ``HamiltonianCycle.validate`` and
produces a dictionary compatible with the ``Sat`` problem definition.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple

from problems import HamiltonianCycle, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` to a SAT variable (1‑based)."""
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    The returned instance is a dict ``{"num_vars": m, "clauses": [...]}``
    satisfying the format required by :class:`Sat`.
    """
    # Validate source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # Edge case: n <= 2 => always NO. Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}  # empty clause = unsat

    # Build adjacency set for quick lookup.
    adj = {frozenset(e) for e in edges}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two different vertices.
    for i in range(n):
        for v, w in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 3. Each vertex appears in exactly one position.
    for v in range(n):
        # at least once
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
        # at most once
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 4. Non‑edges cannot be consecutive in the cycle.
    # For every unordered pair (u, v) that is NOT an edge, forbid both orders.
    all_pairs = {frozenset((u, v)) for u in range(n) for v in range(u + 1, n)}
    non_edges = all_pairs - adj
    for pair in non_edges:
        u, v = tuple(pair)
        for i in range(n):
            j = (i + 1) % n
            # forbid u at i and v at j
            clauses.append([-_var_index(i, u, n), -_var_index(j, v, n)])
            # also forbid v at i and u at j (the same non‑edge in reverse)
            clauses.append([-_var_index(i, v, n), -_var_index(j, u, n)])

    # Validate target instance before returning.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

