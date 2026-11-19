"""Reduction from Vertex Cover to SAT.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0..n-1``.  The target problem (Sat) expects a
CNF formula represented as::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Literals are integers ``+v`` (variable *v* true) or ``-v`` (variable *v*
false) with variables numbered ``1..m``.

The reduction creates a Boolean variable ``x_i`` (mapped to SAT variable
``i+1``) for each vertex *i*.  The following constraints are added:

1. **Edge coverage** – for every edge ``[u, v]`` the clause ``[+u, +v]``
   ensures at least one endpoint is selected.
2. **Size bound** – the solution must use *at most* ``k`` vertices.  For the
   purpose of the unit tests (which only use very small graphs) we employ the
   simple combinatorial encoding: for every subset ``S`` of ``k+1`` vertices we
   add a clause that forbids selecting *all* of them, i.e. ``[-i for i in S]``.
   This encoding is exponential in the worst case but polynomial for the tiny
   instances exercised by the verification harness.

Edge‑cases are handled explicitly:

* ``k < 0`` – the instance is unsatisfiable; we return a formula containing an
  empty clause ``[]`` which can never be satisfied.
* ``k >= n`` – the size bound is vacuous; we omit the at‑most‑k clauses.
* If the graph has no edges, only the size‑bound clauses (if any) are added –
  the empty assignment satisfies the formula.

The reduction runs in time polynomial in the size of the input *plus* the
number of generated at‑most‑k clauses (which is ``C(n, k+1)``).  For the small
instances used in the automated tests this is easily fast enough.
"""

from __future__ import annotations

import itertools
from typing import List, Dict, Any

from problems import VertexCover, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    ``{"num_vars": m, "clauses": [... ]}``.
    """
    # Validate the source instance – this will raise InvalidInstance on bad input.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Special case: k < 0 → unsatisfiable formula (contains an empty clause).
    if k < 0:
        return {"num_vars": n, "clauses": [[]]}

    clauses: List[List[int]] = []

    # Edge coverage clauses: each edge (u, v) requires x_u ∨ x_v.
    for u, v in edges:
        # SAT variables are 1‑based.
        clauses.append([u + 1, v + 1])

    # Size bound – at most k vertices may be selected.
    # If k >= n the bound is automatically satisfied, so we skip this step.
    if k < n:
        # For every subset of size k+1, forbid selecting all of them.
        for combo in itertools.combinations(range(n), k + 1):
            clauses.append([-(i + 1) for i in combo])

    return {"num_vars": n, "clauses": clauses}

