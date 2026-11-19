"""Reduction from Clique to SAT.

The source problem is defined in ``problems.py`` as ``Clique`` with the
instance format ``{"n": n, "edges": [[u, v], ...], "k": k}``.
The target problem is SAT with instance format ``{"num_vars": m,
"clauses": [[literal, ...], ...]}`` where literals are signed integers.

We implement a classic polynomial‑time many‑one reduction that creates a
boolean variable ``x_{i,p}`` meaning *vertex* ``i`` occupies *position* ``p``
in the size‑``k`` clique (positions are numbered 0 … k‑1).  The reduction
produces a CNF formula that is satisfiable exactly when the original graph
contains a clique of size at least ``k``.

Edge cases are handled directly without constructing a large formula:

* ``k <= 0`` – always a yes instance → return an empty formula (no clauses).
* ``k == 1`` and ``n >= 1`` – always yes → also return an empty formula.
* ``k > n`` – impossible → return a formula containing a single empty
  clause, which is unsatisfiable.

For the non‑trivial case (``1 < k <= n``) we generate the following constraints
as CNF clauses:

1. **Each position is occupied** – for every position ``p`` a clause that at
   least one vertex is placed there.
2. **A vertex appears in at most one position** – for each vertex ``i`` and
   every pair of distinct positions ``p < q`` a clause ``(-x_{i,p} ∨ -x_{i,q})``.
3. **At most one vertex per position** – for each position ``p`` and every
   pair of distinct vertices ``i < j`` a clause ``(-x_{i,p} ∨ -x_{j,p})``.
   Together with (1) this forces exactly one vertex per position.
4. **Non‑edges are forbidden** – for every unordered pair of vertices ``i``
   and ``j`` that is *not* an edge, and for every pair of (possibly equal)
   positions ``p, q`` we add ``(-x_{i,p} ∨ -x_{j,q})``.  Because (3) already
   prevents ``p == q`` when ``i != j``, we could restrict to ``p != q``; the
   simpler implementation adds the clause for all ``p, q`` which is still
   polynomial.

The number of variables is ``n * k`` (indexed from 1 as required by the SAT
format).  All clauses are represented as lists of integers where a positive
integer denotes the corresponding variable being true and a negative integer
denotes it being false.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # ----- Edge‑case handling ------------------------------------------------
    if k <= 0:
        # Empty formula is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Any non‑empty graph (or even an empty graph with n==0) has a 1‑clique
        # iff n >= 1. The specification states k==1 is yes whenever n>=1, and
        # when n==0 the instance is trivially no because k>n, which is handled
        # by the next condition.
        if n >= 1:
            return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # ----- Build the reduction ---------------------------------------------
    # Variable indexing: x_{i,p} -> var = i * k + p + 1 (1‑based).
    num_vars = n * k
    clauses: List[List[int]] = []

    # Helper to compute variable id.
    def var(i: int, p: int) -> int:
        return i * k + p + 1

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [var(i, p) for i in range(n)]
        clauses.append(clause)

    # 2. A vertex appears in at most one position.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-var(i, p), -var(i, q)])

    # 3. At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, p), -var(j, p)])

    # Prepare a fast edge‑lookup set.
    edge_set = {frozenset((u, v)) for u, v in edges}

    # 4. For every non‑edge, forbid both vertices being selected.
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) not in edge_set:
                for p in range(k):
                    for q in range(k):
                        clauses.append([-var(i, p), -var(j, q)])

    return {"num_vars": num_vars, "clauses": clauses}

