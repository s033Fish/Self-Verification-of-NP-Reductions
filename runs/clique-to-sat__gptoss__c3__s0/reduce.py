"""Reduction from Clique to SAT.

The source problem is :class:`problems.Clique` and the target is
``problems.Sat``.  Both classes are imported from ``problems.py`` which also
provides validation and a brute‑force ``is_yes`` method that we can use in the
tests.

The reduction follows the classic polynomial‑time encoding of the *k‑Clique*
problem into a CNF formula:

* Variables ``x_{i,v}`` (``i`` = position in the clique, ``v`` = vertex) are
  true iff vertex ``v`` occupies position ``i`` of a size‑``k`` clique.
* For each position we add a clause requiring *some* vertex to be placed there.
* For each position we forbid two different vertices from occupying the same
  position (pairwise at‑most‑one constraints).
* For each vertex we forbid it from appearing in two different positions.
* For every non‑edge ``{u, v}`` we forbid the two vertices from being chosen
  simultaneously in the clique (for all ordered pairs of positions).

The encoding uses ``k * n`` Boolean variables where ``n`` is the number of
vertices.  Variable numbers start at ``1`` as required by the SAT instance
format.  The function ``reduce`` handles the edge‑cases described in the
Clique specification directly:

* ``k <= 0`` – always a *yes* instance → return a trivially satisfiable SAT
  instance (zero variables, no clauses).
* ``k == 1`` and ``n >= 1`` – also always *yes* → same trivial formula.
* ``k > n`` – always *no* → return an unsatisfiable SAT instance consisting
  of a single empty clause.

The produced SAT instance respects the format required by ``Sat.validate``:
``{"num_vars": m, "clauses": [[l1, l2, ...], ...]}`` where literals are
positive for true and negative for false.
"""

from __future__ import annotations

from typing import List, Dict

from problems import SOURCE, TARGET


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` (0‑based) and vertex ``v`` (0‑based) to a SAT variable.

    Variables are numbered from 1 to ``k * n``.  The formula uses the ordering
    ``i * n + v + 1`` which is easy to invert if needed.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a SAT instance.

    The returned instance satisfies ``TARGET.validate`` and has the property
    that ``TARGET.is_yes`` returns the same truth value as ``SOURCE.is_yes``
    for the original instance.
    """
    # Validate the source instance (may raise InvalidInstance).
    SOURCE.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling according to the Clique specification.
    if k <= 0:
        # Always yes → empty formula (no variables, no clauses).
        return {"num_vars": 0, "clauses": []}
    if k == 1 and n >= 1:
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no → unsatisfiable formula with a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick edge lookup.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: List[List[int]] = []

    # 1. At least one vertex per position.
    for i in range(k):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position (pairwise mutual exclusion).
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 3. Each vertex appears at most once (cannot occupy two positions).
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 4. Non‑edges cannot both be selected.
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) in edge_set:
                continue  # edge exists, no restriction needed
            for i in range(k):
                for j in range(k):
                    clauses.append([-_var_index(i, u, n), -_var_index(j, v, n)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}
