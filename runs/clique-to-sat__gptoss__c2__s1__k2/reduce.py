"""Reduction from Clique to SAT.

The source problem is ``Clique`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is ``Sat`` with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction follows the classic polynomial‑time transformation using a
binary variable ``x_{i,v}`` that is true iff vertex ``v`` occupies the ``i``‑th
position of a potential clique of size ``k``.  The constraints ensure that:

1. Every position is filled by *some* vertex.
2. No position contains more than one vertex.
3. No vertex appears in two different positions.
4. Chosen vertices are pairwise adjacent (i.e. form a clique).

Edge‑cases are handled directly:

* ``k <= 0`` – always a yes instance, mapped to an empty SAT formula (which is
  trivially satisfiable).
* ``k == 1`` and ``n >= 1`` – also always yes; we reuse the empty formula.
* ``k > n`` – impossible to have such a clique, mapped to a formula containing
  a single empty clause, which is unsatisfiable.

The function ``reduce`` runs in time polynomial in ``n`` and ``k`` and produces
an instance that is satisfiable iff the original graph contains a clique of at
least size ``k``.
"""

from __future__ import annotations

from typing import Dict, List, Set


def _var_id(i: int, v: int, n: int) -> int:
    """Return a unique SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 upwards as required by the SAT format.
    ``i`` is in ``0..k-1`` and ``v`` in ``0..n-1``.  The mapping ``i * n + v + 1``
    is a simple bijection.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described in
        the problem statement.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ----------------------------------------------------
    if k <= 0:
        # Empty formula – always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1 and n >= 1:
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    # Normal case -----------------------------------------------------------
    # Build a set for O(1) edge look‑ups.
    edge_set: Set[frozenset] = {frozenset(e) for e in edges}

    num_vars = k * n
    clauses: List[List[int]] = []

    # 1. At least one vertex in each position i.
    for i in range(k):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position.
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 3. A vertex cannot occupy two different positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 4. Non‑edges forbid simultaneous selection.
    for i in range(k):
        for j in range(i + 1, k):
            for v in range(n):
                for w in range(n):
                    if v == w:
                        continue  # already excluded by (3)
                    if frozenset({v, w}) not in edge_set:
                        clauses.append([-_var_id(i, v, n), -_var_id(j, w, n)])

    return {"num_vars": num_vars, "clauses": clauses}

# The module is intended to be imported by the evaluation harness.  No
# top‑level test code is included to keep the file minimal and side‑effect
# free.
