"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`problems.HamiltonianPath` and the target is
``problems.Sat``.  The reduction follows the classic encoding that uses a
boolean variable ``x_{i,v}`` to indicate that vertex ``v`` occupies position
``i`` in the Hamiltonian path (positions are ``0`` … ``n-1``).  The SAT formula
is satisfiable iff such an assignment exists, i.e. iff the graph has a
Hamiltonian path.

The encoding is polynomial‑time and produces at most ``O(n^2 + n·|E|)``
clauses, where ``n`` is the number of vertices.

Edge cases are handled explicitly:

* ``n = 0`` – the Hamiltonian‑Path instance is a definite **no**.  We return a
  formula that is unsatisfiable by including an empty clause.
* ``n = 1`` – the instance is a definite **yes**.  We return an empty formula
  (no clauses) which is trivially satisfiable.

The public API required by the task is a single function ``reduce`` that
accepts a source instance (a ``dict``) and returns a target instance (also a
``dict``) in the formats defined in ``problems.py``.
"""

from __future__ import annotations

from typing import List

from problems import HamiltonianPath, Sat


def _var_id(i: int, v: int, n: int) -> int:
    """Map a position ``i`` and vertex ``v`` to a 1‑based SAT variable.

    The encoding uses exactly ``n * n`` variables, numbered from ``1``.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: dict) -> dict:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    The returned dictionary conforms to the ``Sat`` specification:
    ``{"num_vars": m, "clauses": [[...], ...]}``.
    """
    # Validate the source instance (will raise if malformed).
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case handling ---------------------------------------------------
    if n == 0:
        # No vertices → no Hamiltonian path. Return an unsatisfiable formula.
        # A single empty clause is enough.
        return {"num_vars": 1, "clauses": [[]]}
    if n == 1:
        # Trivial yes – empty formula (no clauses) is satisfiable.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency set for quick lookup of existing edges.
    adj = {frozenset((u, v)) for u, v in edges}

    clauses: List[List[int]] = []
    m = n * n  # total number of variables

    # 1. Each position i must contain at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i contains at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 3. Each vertex v appears in at least one position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex v appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 5. Edge consistency: consecutive positions must correspond to an edge.
    # For every ordered pair (u, v) that is NOT an edge, forbid u at i and v at i+1.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if frozenset((u, v)) not in adj:
                    # u and v are not adjacent → cannot be consecutive.
                    clauses.append([-_var_id(i, u, n), -_var_id(i + 1, v, n)])

    # Return the SAT instance.
    return {"num_vars": m, "clauses": clauses}

