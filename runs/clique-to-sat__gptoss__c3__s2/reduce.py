"""Reduction from Clique to SAT.

The source problem is :class:`Clique` (graph with a target clique size ``k``).
The target problem is :class:`Sat` (CNF satisfiability).

We use the classic encoding with variables ``x_{i,v}`` meaning *vertex* ``v``
occupies *position* ``i`` in the clique (``i`` ranges from ``0`` to ``k-1``).

Constraints encoded as clauses:

1. **Each position chooses at least one vertex** – a single clause per
   position containing all variables for that position.
2. **A vertex cannot appear in two different positions** – for every vertex
   ``v`` and every pair of positions ``i < j`` we add the clause
   ``(-x_{i,v} ∨ -x_{j,v})``.
3. **Chosen vertices must be pairwise adjacent** – for every unordered pair
   of distinct vertices ``u, v`` that are *not* an edge we forbid selecting them
   simultaneously in any two positions.  For each ordered pair of positions
   ``i < j`` we add ``(-x_{i,u} ∨ -x_{j,v})`` and ``(-x_{i,v} ∨ -x_{j,u})``.

The encoding is polynomial in ``n`` (number of vertices) and ``k`` (clique
size).  Edge‑cases from the specification are handled explicitly:

* ``k <= 0`` – always a yes instance.  We return an empty CNF (no clauses),
  which is satisfiable by definition.
* ``k > n`` – always a no instance.  We return a formula containing a single
  empty clause ``[]`` which is unsatisfiable.
* ``n == 0`` is covered by the above rules.

The function ``reduce`` follows the required signature ``reduce(instance) ->
instance`` where the input is a Clique instance and the output a Sat instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import problem classes for type hints / validation side‑effects.
from problems import Clique, Sat  # noqa: F401


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    SAT variables are 1‑based, so we add ``1``.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned dictionary follows the format required by :class:`Sat`:
    ``{"num_vars": m, "clauses": [[l1, l2, ...], ...]}``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases per Clique specification.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Set of edges for O(1) lookup.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: List[List[int]] = []

    # 1. Each position must choose at least one vertex.
    for i in range(k):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No vertex appears in two positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Non‑edges cannot both be chosen.
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) in edge_set:
                continue
            for i in range(k):
                for j in range(i + 1, k):
                    clauses.append([-_var_index(i, u, n), -_var_index(j, v, n)])
                    clauses.append([-_var_index(i, v, n), -_var_index(j, u, n)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

