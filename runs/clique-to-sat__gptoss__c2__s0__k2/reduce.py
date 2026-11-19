"""Reduction from Clique to SAT.

The source problem ``Clique`` is defined in ``problems.py`` with the
following instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled ``0`` … ``n-1``), ``edges``
contains each undirected edge exactly once and ``k`` is the required size of
the clique.

The target problem ``Sat`` expects a CNF formula in the format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1`` … ``m`` and a *literal* is a signed integer –
positive for the variable itself, negative for its negation.

The classic polynomial‑time reduction encodes the existence of a clique of
size ``k`` using Boolean variables ``x_{i,v}`` meaning “vertex *v* occupies the
*i*-th position of the clique” (``i`` ranges from ``0`` … ``k-1``).  The
following constraints are translated into clauses:

1. **Each position is occupied by at least one vertex.**
   For every ``i`` we add the clause ``(x_{i,0} ∨ x_{i,1} ∨ … ∨ x_{i,n-1})``.

2. **No position contains two distinct vertices.**
   For each ``i`` and each unordered pair ``u < v`` we add the clause
   ``(¬x_{i,u} ∨ ¬x_{i,v})``.

3. **A vertex cannot appear in two different positions.**
   For each vertex ``v`` and each pair of positions ``i < j`` we add
   ``(¬x_{i,v} ∨ ¬x_{j,v})``.

4. **Non‑edges cannot both be selected.**
   For every pair of vertices ``u, v`` that are *not* connected by an edge
   (including ``u == v``) and for every pair of distinct positions ``i != j``
   we add ``(¬x_{i,u} ∨ ¬x_{j,v})``.  This guarantees that any two selected
   vertices are adjacent.

Edge cases are handled explicitly so that the reduction respects the
definition of ``Clique.is_yes``:

* ``k <= 0`` – always a yes instance.  We output an empty formula (no clauses),
  which is trivially satisfiable.
* ``k == 1`` and ``n >= 1`` – also always yes.  The same empty formula works.
* ``k > n`` – always a no instance.  We output a formula consisting of a
  single empty clause ``[]``; such a clause can never be satisfied.

The implementation runs in time polynomial in ``n`` and ``k`` and uses only
basic Python data structures.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

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

    # Edge‑case handling ----------------------------------------------------
    if k <= 0:
        # Empty formula – always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # A single vertex always forms a clique if at least one vertex exists.
        # The instance definition guarantees n >= 1 for a meaningful graph.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for O(1) edge queries.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        adj.add((u, v))

    # Helper to map (position i, vertex v) to a SAT variable number (1‑based).
    def var(i: int, v: int) -> int:
        return i * n + v + 1  # +1 because SAT variables start at 1

    num_vars = k * n
    clauses: List[List[int]] = []

    # 1. Each position i must contain at least one vertex.
    for i in range(k):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two distinct vertices.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # 3. A vertex cannot appear in two different positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # 4. Non‑edges cannot both be selected.
    # For each unordered pair of vertices that are not adjacent, forbid them
    # from occupying two distinct positions.
    # We also forbid the same vertex being selected twice (already covered by
    # constraint 3), but including u == v here does no harm.
    for u in range(n):
        for v in range(n):
            # Determine if (u, v) is a non‑edge (including self‑loops).
            a, b = (u, v) if u <= v else (v, u)
            if a == b or (a, b) not in adj:
                # For every ordered pair of distinct positions i != j.
                for i in range(k):
                    for j in range(k):
                        if i == j:
                            continue
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}

