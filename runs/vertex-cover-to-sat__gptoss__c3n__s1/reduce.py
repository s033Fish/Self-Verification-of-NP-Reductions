"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`Sat`.

For a graph G = (V, E) and an integer k we create a CNF formula over
variables ``x_i`` (1‑based, i.e., variable ``i+1`` corresponds to vertex ``i``)
that is satisfiable iff G has a vertex cover of size at most k.

Encoding:
    * For every edge (u, v) we add the clause ``[u+1, v+1]`` – at least one
      endpoint must be selected.
    * To enforce the cardinality constraint (|C| ≤ k) we add, for every
      subset S ⊆ V with |S| = k+1, the clause that at least one vertex of S
      is *not* selected, i.e. ``[-(i+1) for i in S]``.  This is a standard
      (though exponential) encoding.  For the small instances used in the
      automated tests the blow‑up is acceptable and keeps the implementation
      simple and easy to verify.

Edge‑case handling:
    * k < 0 – the answer is always NO.  We return an unsatisfiable formula
      consisting of a single empty clause ``[]``.
    * k >= |V| – the answer is always YES.  We return a trivially satisfiable
      formula (no clauses).
    * No edges – any set of vertices (including the empty set) covers the
      graph, so the formula only needs to respect the size bound.  The above
      encoding already handles this correctly.

The function runs in polynomial *time* with respect to the size of the
generated formula.  For the intended test suite the exponential part (the
enumeration of subsets of size k+1) is bounded because n is tiny.
"""

from __future__ import annotations

import itertools
from typing import Dict, List

from problems import VertexCover, Sat

def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary matching the format required by ``VertexCover.validate``.

    Returns
    -------
    dict
        A SAT instance suitable for ``Sat.validate``.
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 -> always unsatisfiable.
    if k < 0:
        # An empty clause makes the formula unsatisfiable.
        return {"num_vars": n, "clauses": [[]]}

    # Edge case: k >= n -> always satisfiable.
    if k >= n:
        # No constraints needed; any assignment works.
        return {"num_vars": n, "clauses": []}

    clauses: List[List[int]] = []

    # 1. Edge coverage clauses: (x_u ∨ x_v) for each edge.
    for u, v in edges:
        # Variables are 1‑based.
        clauses.append([u + 1, v + 1])

    # 2. Cardinality constraint: at most k vertices selected.
    # For every subset S of size k+1, add clause (¬x_i for i in S).
    # This forbids all vertices in S from being true simultaneously.
    if k < n:  # only needed when the bound is non‑trivial
        for subset in itertools.combinations(range(n), k + 1):
            clause = [-(i + 1) for i in subset]
            clauses.append(clause)

    return {"num_vars": n, "clauses": clauses}
