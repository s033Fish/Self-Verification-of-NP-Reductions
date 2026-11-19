"""Reduction from Clique to SAT.

The source problem is :class:`Clique` defined in ``problems.py``.
The target problem is :class:`Sat`.

The reduction follows the classic polynomial‑time encoding of the k‑Clique
problem into a CNF formula.

For a graph G = (V, E) with |V| = n and an integer k, we create Boolean
variables ``x_{i,p}`` meaning that vertex ``i`` occupies position ``p`` in a
potential clique (positions are 0‑based).  The variable index in the SAT
instance is ``i * k + p + 1`` (SAT variables are 1‑based).

Constraints encoded as clauses:

1. **Each position is occupied** – for every position ``p`` there is a clause
   ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n‑1,p})``.
2. **At most one vertex per position** – for each position ``p`` and any two
   distinct vertices ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.
3. **A vertex appears at most once** – for each vertex ``i`` and any two
   distinct positions ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.
4. **Non‑edges cannot both be chosen** – for every unordered pair of
   vertices ``(i, j)`` that is *not* an edge and for all positions ``p, q`` we
   add ``(¬x_{i,p} ∨ ¬x_{j,q})``.

Edge‑case handling:

* ``k <= 0`` – always a yes instance.  We return a SAT instance with *no*
  clauses, which is trivially satisfiable.
* ``k == 1`` – yes iff the graph contains at least one vertex.  When ``n >= 1``
  we return a single‑variable formula ``[1]``; otherwise we return an empty
  clause making the formula unsatisfiable.
* ``k > n`` – always no.  We return a formula containing a single empty
  clause ``[]`` which is unsatisfiable.

The function runs in time polynomial in ``n`` and ``k`` (the number of
variables is ``n * k`` and the number of clauses is ``O(n^2 * k^2)``).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Return a set containing each undirected edge as a frozenset.

    ``edges`` is the list from a Clique instance.  The function assumes the
    instance has already been validated.
    """
    return {frozenset(e) for e in edges}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a SAT instance.

    The returned dictionary follows the format required by :class:`Sat`.
    """
    # Validate source instance (raises InvalidInstance on failure).
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling before building the generic encoding.
    if k <= 0:
        # Empty clause list is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # k == 1 is a yes‑instance only when there is at least one vertex.
        if n >= 1:
            return {"num_vars": 1, "clauses": [[1]]}
        return {"num_vars": 0, "clauses": [[]]}
    if k > n:
        # Unsatisfiable: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    # General case.
    num_vars = n * k
    clauses: List[List[int]] = []

    # Helper to map (i, p) -> variable index (1‑based).
    def var(i: int, p: int) -> int:
        return i * k + p + 1

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [var(i, p) for i in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, p), -var(j, p)])

    # 3. A vertex appears at most once.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-var(i, p), -var(i, q)])

    # 4. Non‑edges cannot both be selected.
    edge_set = _edge_set(edges)
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) not in edge_set:
                for p in range(k):
                    for q in range(k):
                        clauses.append([-var(i, p), -var(j, q)])

    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

