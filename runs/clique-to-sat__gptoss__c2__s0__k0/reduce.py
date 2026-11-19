"""Reduction from Clique to SAT.

This module implements a polynomial‑time many‑one reduction from the
Clique decision problem to Boolean satisfiability (CNF‑SAT).  The source
problem instance follows the format described in ``problems.py`` for the
``Clique`` class, and the target instance follows the format for the
``Sat`` class.

The reduction encodes the existence of a clique of size *k* in a graph
with *n* vertices using Boolean variables ``x_{i}^{v}`` meaning “vertex
``v`` occupies position ``i`` in the clique”.  The encoding uses the
standard constraints:

1. **Each position is occupied by at least one vertex.**
2. **No vertex occupies two different positions.**
3. **No two distinct vertices occupy the same position.**
4. **If two vertices are not adjacent, they cannot both be selected**
   (i.e., cannot appear in the clique at any two positions).

All constraints are expressed as clauses in conjunctive normal form.
Variable numbering is deterministic: for position ``i`` (0‑based) and
vertex ``v`` (0‑based) the variable id is ``i * n + v + 1``.  This yields
``k * n`` variables in total.

Edge cases are handled directly:

* ``k <= 0`` – the answer is always *yes*; we return a trivially
  satisfiable formula with no variables and no clauses.
* ``k == 1`` and ``n >= 1`` – also always *yes*; the same trivial
  formula is returned.
* ``k > n`` – impossible to have such a clique; we return an
  unsatisfiable formula consisting of a single empty clause.

The function ``reduce`` performs the conversion and runs in polynomial
time with respect to ``n`` and ``k``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _variable_id(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to ``k * n`` as required by the SAT
    format.  ``i`` and ``v`` are zero‑based indices, ``n`` is the number of
    vertices.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as
        specified in the ``Clique`` problem definition.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and
        ``"clauses"``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ---------------------------------------------------
    if k <= 0:
        # Trivially satisfiable: no variables, no clauses.
        return {"num_vars": 0, "clauses": []}
    if k == 1 and n >= 1:
        # Any single vertex forms a clique of size 1.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula – a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    # Build a set of undirected edges for constant‑time lookup.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    num_vars = k * n
    clauses: List[List[int]] = []

    # 1. Each position i must contain at least one vertex.
    for i in range(k):
        clause = [_variable_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No vertex appears in two different positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                vi = _variable_id(i, v, n)
                vj = _variable_id(j, v, n)
                clauses.append([-vi, -vj])

    # 3. No two distinct vertices occupy the same position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                ui = _variable_id(i, u, n)
                vi = _variable_id(i, v, n)
                clauses.append([-ui, -vi])

    # 4. Non‑edges cannot both be selected in the clique.
    #    For every non‑adjacent pair (u, v) and for every ordered pair of
    #    distinct positions (i, j) we add the clause ¬x_i^u ∨ ¬x_j^v.
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) in edge_set:
                continue
            for i in range(k):
                for j in range(k):
                    if i == j:
                        continue
                    ui = _variable_id(i, u, n)
                    vj = _variable_id(j, v, n)
                    clauses.append([-ui, -vj])

    return {"num_vars": num_vars, "clauses": clauses}

