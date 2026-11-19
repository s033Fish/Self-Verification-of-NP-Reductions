"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`problems.HamiltonianPath` and the target is
``problems.Sat``.  The reduction follows the classic textbook encoding using
variables ``x_{i,v}`` meaning *vertex ``v`` occupies position ``i`` in the
Hamiltonian path*.

For a graph with ``n`` vertices we create ``n * n`` Boolean variables, numbered
from ``1`` to ``n*n`` (the SAT instance expects variables numbered starting at 1).
The variable index for ``(i, v)`` is ``i * n + v + 1``.

Constraints encoded as CNF clauses:

1. **Each position contains exactly one vertex** – a clause guaranteeing at
   least one vertex at each position and pairwise clauses forbidding two
   vertices simultaneously.
2. **Each vertex appears exactly once** – analogous clauses for each vertex.
3. **Adjacency** – for every pair of vertices that are *not* connected by an
   edge, we forbid them from being consecutive in the path.

Edge cases:

* ``n == 0`` – the answer is always *no*.  We output an unsatisfiable formula
  consisting of a single empty clause ``[]``.
* ``n == 1`` – the answer is always *yes*.  An empty CNF (no clauses) is
  trivially satisfiable.

The reduction runs in polynomial time (``O(n^3)`` clauses) and complies with
the validation helpers defined in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, Sat


def _var(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to ``n*n`` inclusive.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    The function validates the input using ``HamiltonianPath.validate`` and
    returns a dictionary suitable for ``Sat.validate``.
    """
    # Validate source instance.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge set for O(1) look‑ups; store as frozenset of the two endpoints.
    edge_set = {frozenset(edge) for edge in edges}

    # Edge case handling.
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable: no clauses needed.
        return {"num_vars": 1, "clauses": []}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has exactly one vertex.
    for i in range(n):
        # At least one vertex in position i.
        clauses.append([_var(i, v, n) for v in range(n)])
        # At most one vertex: pairwise negative clauses.
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # 2. Each vertex appears exactly once.
    for v in range(n):
        # At least once.
        clauses.append([_var(i, v, n) for i in range(n)])
        # At most once.
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # 3. Non‑edges cannot be consecutive.
    # For each pair of distinct vertices that are not connected, forbid them
    # from appearing consecutively in either order.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    # forbid u at i and v at i+1
                    clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])
                    # forbid v at i and u at i+1 (the opposite direction)
                    clauses.append([-_var(i, v, n), -_var(i + 1, u, n)])

    return {"num_vars": num_vars, "clauses": clauses}

