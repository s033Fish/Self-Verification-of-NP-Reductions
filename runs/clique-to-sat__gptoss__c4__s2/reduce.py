"""Reduction from Clique to SAT.

The source problem is :class:`Clique` defined in ``problems.py``. The target
problem is :class:`Sat`.

The reduction follows the classic textbook construction using a variable
``x_{i,p}`` that is true iff vertex *i* occupies position *p* in a clique of
size *k*.

Constraints encoded as CNF clauses:

1. **Each position is occupied** – for every position ``p`` (1‑based) there is a
   clause containing all ``x_{i,p}`` for ``i`` in ``0..n-1``.
2. **At most one vertex per position** – for each position ``p`` and each pair
   of distinct vertices ``i < j`` we add ``¬x_{i,p} ∨ ¬x_{j,p}``.
3. **A vertex appears at most once** – for each vertex ``i`` and each pair of
   positions ``p < q`` we add ``¬x_{i,p} ∨ ¬x_{i,q}``.
4. **Non‑edges are forbidden** – for every unordered non‑edge ``{i, j}`` and
   every pair of positions ``p, q`` we add ``¬x_{i,p} ∨ ¬x_{j,q}``.

The number of variables is ``n * k`` and the number of clauses is
polynomial in ``n`` and ``k``.

Edge‑case handling:

* ``k <= 0`` – always a *yes* instance. We return a trivially satisfiable SAT
  formula (zero variables, no clauses).
* ``k > n`` – always a *no* instance. We return an unsatisfiable formula, e.g.
  a single variable with an empty clause.

The function validates the input using ``Clique.validate`` and returns a
dictionary matching the SAT instance format.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import Clique, Sat, InvalidInstance


def _var_id(i: int, p: int, k: int) -> int:
    """Map vertex ``i`` (0‑based) and position ``p`` (1‑based) to a SAT variable.

    Variables for SAT are 1‑based, so we compute ``i * k + p`` which yields a
    number in ``1..n*k``.
    """

    return i * k + p


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned instance satisfies the SAT format required by ``Sat``.
    """

    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases defined in the problem statement.
    if k <= 0:
        # Always yes – return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no – return an unsatisfiable formula (empty clause).
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for quick lookup of edges.
    adjacency = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacency[u][v] = adjacency[v][u] = True

    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex.
    for p in range(1, k + 1):
        clause = [_var_id(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position.
    for p in range(1, k + 1):
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_id(i, p, k), -_var_id(j, p, k)])

    # 3. A vertex appears at most once (cannot occupy two positions).
    for i in range(n):
        for p, q in combinations(range(1, k + 1), 2):
            clauses.append([-_var_id(i, p, k), -_var_id(i, q, k)])

    # 4. Non‑edges cannot both be selected.
    # Enumerate unordered pairs (i, j) that are NOT edges and i != j.
    for i in range(n):
        for j in range(i + 1, n):
            if not adjacency[i][j]:
                for p in range(1, k + 1):
                    for q in range(1, k + 1):
                        clauses.append([-_var_id(i, p, k), -_var_id(j, q, k)])

    return {"num_vars": n * k, "clauses": clauses}

