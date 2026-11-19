"""Reduction from Clique to SAT.

The source problem is :class:`problems.Clique` and the target is
``problems.Sat``.  The reduction follows the classic textbook encoding of the
``k``‑clique problem as a CNF formula.

We introduce a Boolean variable ``x_{i,v}`` meaning *vertex ``v`` occupies the
``i``‑th position of the clique* (positions are numbered ``0..k-1``).  The
variables are numbered from ``1`` as required by the SAT instance format.

Constraints encoded as clauses:

1. **Each position is occupied by at least one vertex** – a clause that is the
   disjunction of all ``x_{i,v}`` for a fixed ``i``.
2. **No position contains two different vertices** – for each ``i`` and each
   distinct ``u, v`` we add ``(¬x_{i,u} ∨ ¬x_{i,v})``.
3. **A vertex cannot appear in two positions** – for each vertex ``v`` and
   each distinct ``i, j`` we add ``(¬x_{i,v} ∨ ¬x_{j,v})``.
4. **Non‑edges are forbidden** – if ``{u, v}`` is *not* an edge then the two
   vertices cannot both be chosen, i.e. for every ordered pair of positions
   ``i < j`` we add ``(¬x_{i,u} ∨ ¬x_{j,v})``.

The construction is polynomial in ``n`` (the number of vertices) and ``k``.

Edge cases required by the specification are handled explicitly:

* ``k <= 0`` – always yes, we output an empty formula (no clauses).
* ``k > n`` – always no, we output a formula containing a single empty clause
  which is unsatisfiable.
* ``k == 1`` with ``n >= 1`` – also always yes, we shortcut to an empty formula.

The ``reduce`` function validates the input (using the source problem's
``validate``) and returns a dictionary suitable for ``Sat``.
"""

from __future__ import annotations

from typing import List, Tuple, Set

import problems


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` (0‑based) and vertex ``v`` (0‑based) to a SAT variable.

    SAT variables are 1‑based, so we add ``1`` at the end.
    """
    return i * n + v + 1


def reduce(instance: dict) -> dict:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned instance obeys the format required by ``problems.Sat``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    problems.Clique.validate(instance)

    n: int = instance["n"]
    k: int = instance["k"]
    edges: List[List[int]] = instance["edges"]

    # Edge‑case handling ----------------------------------------------------
    if k <= 0:
        # Always satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable – a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if k == 1 and n >= 1:
        # A single vertex always forms a 1‑clique.
        return {"num_vars": 0, "clauses": []}

    # General case ----------------------------------------------------------
    # Build a quick lookup for existing edges.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    clauses: List[List[int]] = []

    # 1. At least one vertex per position.
    for i in range(k):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 3. A vertex appears in at most one position.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 4. Non‑edges cannot both be selected.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v:
                        continue
                    a, b = (u, v) if u < v else (v, u)
                    if (a, b) not in edge_set:
                        # (u,v) is not an edge; forbid them in positions i,j.
                        clauses.append([-_var_index(i, u, n), -_var_index(j, v, n)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

