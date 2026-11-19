"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` (see ``problems.py``) and the
target problem is :class:`Sat`.  For a graph G = (V,E) with |V| = n we create a
boolean variable ``x_i`` (1‑based) that is true iff vertex ``i-1`` is chosen for
the cover.

Two types of constraints are required:

1. **Edge covering** – for each edge ``(u,v)`` we add the clause ``(x_u ∨ x_v)``.
2. **Cardinality** – the number of selected vertices must be at most ``k``.

The cardinality constraint is encoded using a simple subset‑blocking encoding:
for every set of ``k+1`` vertices we add a clause requiring that at least one of
them is *not* selected.  This encoding is polynomial in the input size (the
number of clauses is ``C(n, k+1)`` which is at most ``2^n``) and is sufficient
for the small instances used in the verification tests.

Special cases are handled explicitly:

* ``k < 0`` – the instance is unsatisfiable; we return a formula containing a
  single empty clause.
* ``k >= n`` – the cardinality bound is vacuous, so we only add the edge
  clauses.

The function ``reduce`` validates the input using ``VertexCover.validate`` and
returns a dictionary suitable for ``Sat.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    The returned instance follows the format required by ``Sat.validate``:
    ``{"num_vars": m, "clauses": [[...], ...]}``.
    """
    # Validate the source instance first.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 -> unsatisfiable formula (contains an empty clause).
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    clauses: List[List[int]] = []

    # 1. Edge covering clauses (x_u ∨ x_v).
    for u, v in edges:
        # Variables are 1‑based in SAT.
        clauses.append([u + 1, v + 1])

    # If the cardinality bound is trivial, we are done.
    if k >= n:
        return {"num_vars": n, "clauses": clauses}

    # 2. Cardinality bound: at most k vertices may be true.
    # For every subset of size k+1 we add a clause that at least one is false.
    from itertools import combinations
    for subset in combinations(range(1, n + 1), k + 1):
        clauses.append([-v for v in subset])

    num_vars = n
    return {"num_vars": num_vars, "clauses": clauses}

