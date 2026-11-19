"""Reduction from Clique to SAT.

The source problem is :class:`Clique` (graph with a target clique size ``k``).
The target problem is :class:`Sat` (CNF formula).

The reduction follows the classic textbook construction using ``k`` *position*
variables.  For each vertex ``i`` (0‑based) and each position ``p`` in the
potential clique (also 0‑based) we introduce a Boolean variable ``x_{i,p}``
meaning *vertex i occupies position p*.

Constraints encoded as CNF clauses:

1. **Each position is occupied** – for every position ``p`` at least one vertex
   must be placed there:
   ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p})``.

2. **A vertex appears at most once** – for every vertex ``i`` and every pair of
   distinct positions ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.

3. **At most one vertex per position** – for every position ``p`` and every
   pair of distinct vertices ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.
   Together with (1) this forces exactly one vertex per position.

4. **Non‑edges cannot both be selected** – if ``{i, j}`` is *not* an edge of the
   graph then the two vertices cannot both belong to the clique, regardless of
   the positions they occupy.  For every such non‑edge and for all positions
   ``p, q`` we add ``(¬x_{i,p} ∨ ¬x_{j,q})``.

The number of variables is ``n * k``; they are numbered from ``1`` upwards
according to the mapping ``var_id = i * k + p + 1``.

Edge cases are handled explicitly to keep the reduction trivial and to avoid
creating unnecessarily large formulas:

* ``k <= 0`` – the answer is always *yes*; we return an empty CNF (zero
  variables, no clauses), which is satisfiable.
* ``k > n`` – the answer is always *no*; we return a formula with a single
  empty clause ``[]`` (unsatisfiable) and zero variables.

The function validates the input using ``Clique.validate`` and returns a
dictionary that conforms to the ``Sat`` instance format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat


def _var_id(i: int, p: int, k: int) -> int:
    """Return the SAT variable number for vertex *i* in position *p*.

    Variables are numbered from 1 as required by the SAT specification.
    """
    return i * k + p + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Clique`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Sat`` format such that the SAT formula
        is satisfiable iff the original graph contains a clique of size at
        least ``k``.
    """
    # Validate the source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling.
    if k <= 0:
        # Always yes – return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no – return an unsatisfiable formula (single empty clause).
        return {"num_vars": 0, "clauses": [[]]}

    # Build a set for quick edge lookup.
    edge_set = {frozenset((u, v)) for u, v in edges}

    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [_var_id(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. A vertex cannot occupy two different positions.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_id(i, p, k), -_var_id(i, q, k)])

    # 3. At most one vertex per position (together with (1) gives exactly one).
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, p, k), -_var_id(j, p, k)])

    # 4. Non‑edges cannot both be selected.
    # Iterate over all unordered vertex pairs that are NOT edges.
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) in edge_set:
                continue  # they are adjacent – no restriction needed
            for p in range(k):
                for q in range(k):
                    clauses.append([-_var_id(i, p, k), -_var_id(j, q, k)])

    # Return the SAT instance.
    return {"num_vars": num_vars, "clauses": clauses}

