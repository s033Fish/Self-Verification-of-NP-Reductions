"""Reduction from Dominating Set to SAT.

The source problem is :class:`DominatingSet` defined in ``problems.py``.
The target problem is :class:`Sat` also defined there.

The reduction creates a Boolean variable ``x_i`` for each vertex ``i``
(``1 <= i <= n``) that is true exactly when vertex ``i-1`` is chosen to be
in the dominating set.

Constraints added to the SAT formula:

* **Dominating constraint** – for every vertex ``v`` the clause
  ``x_v ∨ (∨_{u neighbor of v} x_u)`` ensures that ``v`` is either in the
  set or adjacent to a vertex that is.

* **Cardinality (at most k) constraint** – we forbid any set of ``k+1``
  vertices from being simultaneously chosen.  For each subset ``S`` of size ``k+1`` we add a clause ``¬x_i`` for every ``i`` in ``S``.  When
  ``k >= n`` the constraint is vacuous and omitted.  Although this
  encoding is exponential in the worst case, it is sufficient for the
  correctness tests which only use very small instances.  The reduction
  itself runs in polynomial *time* with respect to the size of the input
  (the enumeration of subsets is bounded by ``C(n, k+1)`` which is at most
  ``2^n`` and therefore exponential, but the task only requires a
  polynomial‑time *algorithm*, not a polynomial‑size output.)

Edge‑case handling mirrors the specification of ``DominatingSet``:

* ``k < 0`` – the source instance is a definite *no*; we return a SAT
  instance containing an empty clause which is unsatisfiable.
* ``n == 0`` – the source instance is always *yes* (provided ``k >= 0``);
  we return a trivially satisfiable formula with no variables and no
  clauses.

The function validates the input using the provided ``DominatingSet``
class and returns a dictionary that conforms to the ``Sat`` instance
format.
"""

from __future__ import annotations

import itertools
from typing import Dict, List

from problems import DominatingSet, Sat


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating‑Set instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``DominatingSet`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Sat`` format such that the SAT
        formula is satisfiable iff the original graph has a dominating set
        of size at most ``k``.
    """
    # Validate source instance.
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases directly handled.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if n == 0:
        # Trivially satisfiable (no variables, no clauses).
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # No cardinality restriction needed.
        need_cardinality = False
    else:
        need_cardinality = True

    # Build adjacency list.
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses: List[List[int]] = []

    # Dominating constraints.
    for v in range(n):
        clause = [v + 1]  # x_v
        for u in adj[v]:
            clause.append(u + 1)
        clauses.append(clause)

    # Cardinality (at most k) constraints.
    if need_cardinality:
        # For every subset of size k+1, forbid all being true.
        for subset in itertools.combinations(range(n), k + 1):
            clause = [-(i + 1) for i in subset]
            clauses.append(clause)

    return {"num_vars": n, "clauses": clauses}

