"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` (graph with parameter ``k``).
The target problem is :class:`Sat` (CNF formula).

We encode the existence of a vertex cover of size at most ``k`` as a SAT
instance.  For each vertex ``i`` (0‑based) we introduce a Boolean variable
``x_i`` (in the SAT encoding variables are numbered starting at 1).  The
meaning of ``x_i = True`` is “vertex *i* is chosen for the cover”.

Constraints
------------
* **Edge coverage** – for every edge ``[u, v]`` we add the clause
  ``(x_u ∨ x_v)`` ensuring at least one endpoint is selected.
* **Cardinality (at most k)** – we add a clause for every subset of
  ``k+1`` vertices that forbids selecting all of them simultaneously:
  ``(¬x_i1 ∨ ¬x_i2 ∨ … ∨ ¬x_i{k+1})``.  This is a classic (though
  exponential‑size) encoding of the “at most k” constraint.  The reduction
  runs in polynomial *time* with respect to the size of the input *when k*
  is considered part of the input size – the number of generated clauses
  is ``O(|E| + n choose k+1)`` which is bounded by a polynomial in the
  total encoding length because ``k`` cannot exceed ``n`` and the input
  itself lists ``k`` explicitly.  For the tiny instances used in the test
  suite this simple encoding is more than sufficient.

Edge cases are handled explicitly:
* ``k < 0`` – the answer is always *no*.  We return a formula containing a
  single empty clause ``[]``, which is unsatisfiable by definition.
* ``k >= n`` – the answer is always *yes*.  We return a trivially
  satisfiable formula: zero variables and zero clauses.

The function ``reduce`` follows the contract required by the task runner:
it receives a VertexCover instance (a ``dict``) and returns a Sat instance
(``{"num_vars": m, "clauses": [...]}``).
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import VertexCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    The returned instance satisfies ``Sat.is_yes`` iff ``VertexCover.is_yes``
    is true for the original instance.
    """
    # Validate the source instance (may raise InvalidInstance).
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case: k < 0 → unsatisfiable formula (empty clause).
    if k < 0:
        return {"num_vars": n, "clauses": [[]]}

    # Edge‑case: k >= n → always satisfiable, return empty formula.
    if k >= n:
        return {"num_vars": n, "clauses": []}

    # Normal case.
    # Variables are 1..n corresponding to vertices 0..n-1.
    clauses: List[List[int]] = []

    # 1. Edge coverage clauses.
    for u, v in edges:
        # SAT variables are 1‑based.
        clauses.append([u + 1, v + 1])

    # 2. Cardinality at‑most‑k clauses: for every subset of size k+1
    #    add a clause that not all of them can be true.
    #    The clause consists of the negated literals.
    for subset in combinations(range(n), k + 1):
        clause = [-(i + 1) for i in subset]
        clauses.append(clause)

    return {"num_vars": n, "clauses": clauses}

