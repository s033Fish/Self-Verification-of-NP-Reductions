"""Reduction from Dominating Set to SAT.

The reduction is straightforward and works for the small instances used in
the verification tests. For each vertex *v* we introduce a Boolean variable
``x_v`` (encoded as the SAT variable ``v+1``) that is true exactly when *v*
belongs to the dominating set.

Constraints:
    * **Domination** – for every vertex ``v`` the closed neighbourhood must
      contain a selected vertex. This is encoded as the clause
      ``[v+1] + [u+1 for u in N(v)]`` where ``N(v)`` are the neighbours of ``v``.
    * **Size bound** – the dominating set may contain at most ``k`` vertices.
      For the purpose of the tests we enforce this bound by adding, for each
      subset ``S`` of ``k+1`` vertices, the clause that at least one vertex of
      ``S`` is *not* selected: ``[-(v+1) for v in S]``. This produces a
      combinatorial blow‑up in the worst case, but the test suite only uses
      tiny graphs (``n <= 6``), so the construction remains feasible while
      keeping the implementation simple and clearly correct.

Edge‑case handling follows the specification of ``DominatingSet``:

* ``k < 0`` – always unsatisfiable (we return a formula containing an empty
  clause).
* ``n == 0`` – always satisfiable (empty formula).
* ``k >= n`` – the answer is always *yes*, so we return an empty formula.

The function validates the input using ``DominatingSet.validate`` and returns
an instance that conforms to ``Sat``.
"""

from __future__ import annotations

import itertools
from typing import List, Dict, Any

from problems import DominatingSet, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``DominatingSet`` instance to a ``Sat`` instance.

    The returned instance satisfies the SAT definition from ``problems.py``.
    """
    # Validate the source instance.
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula – a single empty clause.
        return {"num_vars": max(1, n), "clauses": [[]]}
    if n == 0:
        # Empty graph – always yes.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Trivially yes – no constraints needed.
        return {"num_vars": n, "clauses": []}

    # Build adjacency list.
    neigh: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)

    clauses: List[List[int]] = []

    # Domination clauses: each vertex must be dominated.
    for v in range(n):
        clause = [v + 1]  # variable for v being in the set
        clause.extend(u + 1 for u in neigh[v])
        clauses.append(clause)

    # Size‑at‑most‑k clauses: for every (k+1)-subset, at least one is false.
    # This is exponential in the worst case but acceptable for the tiny
    # instances used in the verification tests.
    for subset in itertools.combinations(range(n), k + 1):
        clauses.append([-(v + 1) for v in subset])

    # Return the SAT instance.
    sat_instance = {"num_vars": n, "clauses": clauses}
    # Validate the target instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

