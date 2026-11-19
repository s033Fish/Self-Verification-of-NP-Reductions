"""Reduction from Dominating Set to SAT.

The source problem is :class:`DominatingSet` and the target problem is
``Sat`` as defined in ``problems.py``.  The reduction is polynomial in the
size of the input (``n`` vertices, ``m`` edges and the parameter ``k``).

We introduce a Boolean variable ``x_i`` for each vertex ``i`` indicating
whether the vertex belongs to the dominating set.  To enforce that the set
contains *exactly* ``k`` vertices we use a classic “selection per position”
encoding:

* For each position ``p`` (``0 ≤ p < k``) we create a variable ``s_{i,p}``
  meaning *vertex ``i`` occupies position ``p``*.
* Each position must be occupied by at least one vertex – a clause
  ``(s_{0,p} ∨ s_{1,p} ∨ … ∨ s_{n‑1,p})``.
* A vertex may occupy at most one position – for every pair ``p < q`` we
  add ``(¬s_{i,p} ∨ ¬s_{i,q})``.
* At most one vertex per position – for every pair ``i < j`` we add
  ``(¬s_{i,p} ∨ ¬s_{j,p})``.
* ``x_i`` is true iff the vertex appears in *some* position.  This is
  encoded as ``(¬s_{i,p} ∨ x_i)`` for each ``p`` and ``(¬x_i ∨ s_{i,0} ∨ … ∨ s_{i,k‑1})``.

With the variables ``x_i`` we can express domination: for every vertex ``v``
the clause ``(x_v ∨ x_u₁ ∨ … ∨ x_uₙ)`` where the ``u_j`` are the neighbours of
``v`` guarantees that ``v`` is either in the set or adjacent to a vertex in
the set.

Edge‑case handling:
* ``k < 0`` – impossible, we return an unsatisfiable formula ``[[]]``.
* ``k == 0`` and ``n > 0`` – impossible to dominate a non‑empty graph, also
  unsatisfiable.
* ``n = 0`` – the empty graph is trivially dominated; we return a trivially
  satisfiable formula (no variables, no clauses).
* ``k ≥ n`` – any set of all vertices dominates the graph, so we also return a
  trivially satisfiable formula.

The function ``reduce`` validates the input, builds the CNF according to the
scheme above and returns it as a dictionary compatible with the ``Sat``
definition.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import DominatingSet, Sat


def _var_x(i: int) -> int:
    """Variable number for ``x_i`` (selected vertex ``i``)."""
    return i + 1  # SAT variables are 1‑based


def _var_s(i: int, p: int, n: int, k: int) -> int:
    """Variable number for ``s_{i,p}``.

    The first ``n`` variables are the ``x_i`` variables.  The ``s`` variables
    follow consecutively.
    """
    return n + i * k + p + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating‑Set instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the docstring of :class:`DominatingSet`.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}``.
    """
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ---------------------------------------------------
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # Non‑empty graph cannot be dominated with zero vertices.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list -------------------------------------------------
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses: List[List[int]] = []

    # 1. Domination clauses: for each vertex v, (x_v ∨ x_u for u in N(v))
    for v in range(n):
        clause = [_var_x(v)] + [_var_x(u) for u in adj[v]]
        clauses.append(clause)

    # 2. Selection‑per‑position constraints
    # a) Each position p must be occupied by at least one vertex.
    for p in range(k):
        clause = [_var_s(i, p, n, k) for i in range(n)]
        clauses.append(clause)

    # b) A vertex cannot occupy two different positions.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_s(i, p, n, k), -_var_s(i, q, n, k)])

    # c) At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_s(i, p, n, k), -_var_s(j, p, n, k)])

    # d) Link x_i with the s‑variables (equivalence).
    for i in range(n):
        for p in range(k):
            clauses.append([-_var_s(i, p, n, k), _var_x(i)])
        clause = [-_var_x(i)] + [_var_s(i, p, n, k) for p in range(k)]
        clauses.append(clause)

    num_vars = n + n * k
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

