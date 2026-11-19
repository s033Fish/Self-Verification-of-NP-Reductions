"""Reduction from Clique to SAT.

The source problem is :class:`Clique` defined in ``problems.py``.  An instance
has the form ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The target problem is :class:`Sat`.  An instance is a CNF formula expressed as
``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where literals are
integers ``+v`` (variable *v* true) or ``-v`` (variable *v* false).

The reduction is the classic polynomial‑time reduction using variables
``x_{i,p}`` meaning *vertex i is the p‑th member of the clique* (``i`` in
``0..n-1`` and ``p`` in ``1..k``).  The CNF enforces:

1. **Every position is filled** – for each ``p`` we add a clause containing
   ``x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p}``.
2. **A vertex cannot occupy two positions** – for each vertex ``i`` and each
   pair ``p < q`` we add ``¬x_{i,p} ∨ ¬x_{i,q}``.
3. **Non‑edges cannot both be chosen** – for each unordered pair of vertices
   ``{i, j}`` that is *not* an edge and for all ``p, q`` we add
   ``¬x_{i,p} ∨ ¬x_{j,q}``.

Edge‑case handling follows the specification of ``Clique``:

* ``k <= 0`` – always a YES instance.  We return an empty CNF (no clauses) which
  is trivially satisfiable.
* ``k == 1`` and ``n >= 1`` – also always YES; the same empty CNF works.
* ``k > n`` – always NO.  We return a formula containing a single empty clause
  ``[]`` which is unsatisfiable.

The function validates the input using ``Clique.validate`` and returns a
dictionary that conforms to the SAT format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat


def _var_index(i: int, p: int, k: int) -> int:
    """Map vertex ``i`` (0‑based) and position ``p`` (1‑based) to a SAT variable.

    Variables are numbered from 1..n*k as required by the SAT definition.
    """
    return i * k + p  # p starts at 1, so the first variable for vertex i is i*k+1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned instance satisfies the SAT format and has the property that
    it is satisfiable iff the original Clique instance has a clique of size at
    least ``k``.
    """
    # Validate the source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling according to the problem statement.
    if k <= 0:
        # Always yes – empty CNF is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Yes whenever there is at least one vertex.
        if n >= 1:
            return {"num_vars": 0, "clauses": []}
        # n == 0 and k == 1 is impossible because k > n, handled below.
    if k > n:
        # Always no – a single empty clause makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick edge lookup.
    adjacency = [[False] * n for _ in range(n)]
    for u, v in edges:
        adjacency[u][v] = adjacency[v][u] = True

    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Every position p must be occupied by at least one vertex.
    for p in range(1, k + 1):
        clause = [_var_index(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. A vertex cannot occupy two different positions.
    for i in range(n):
        for p in range(1, k + 1):
            for q in range(p + 1, k + 1):
                clauses.append([-_var_index(i, p, k), -_var_index(i, q, k)])

    # 3. Non‑edges cannot both be selected.
    for i in range(n):
        for j in range(i + 1, n):
            if not adjacency[i][j]:
                for p in range(1, k + 1):
                    for q in range(1, k + 1):
                        clauses.append([-_var_index(i, p, k), -_var_index(j, q, k)])

    # Validate the produced SAT instance before returning.
    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

