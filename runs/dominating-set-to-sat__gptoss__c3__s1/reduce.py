"""Reduction from Dominating Set to SAT.

The source problem is :class:`DominatingSet` (graph with a bound *k* on the
size of a dominating set).  The target problem is :class:`Sat` (CNF
satisfiability).

For a graph ``G = (V, E)`` with ``|V| = n`` we introduce a Boolean variable
``x_i`` for each vertex ``i`` (1‑based indexing as required by the SAT
definition).  ``x_i`` is true iff vertex ``i`` is selected into the dominating
set.

Two groups of clauses are needed:

1. **Domination clauses** – for every vertex ``v`` the closed neighbourhood
   ``{v} ∪ N(v)`` must contain a selected vertex:

   ``(x_v ∨ x_u1 ∨ x_u2 ∨ ...)`` where ``u1, u2, ...`` are the neighbours of
   ``v``.

2. **Cardinality constraint** – at most ``k`` of the ``x_i`` may be true.  We
   encode ``∑ x_i ≤ k`` with the classic *sequential counter* encoding due to
   Sinz (2005).  It introduces auxiliary variables ``s[i][j]`` meaning “among the
   first ``i`` vertices at least ``j`` are selected”.  The encoding uses
   ``O(n·k)`` additional variables and a linear number of clauses, which is
   polynomial in the size of the input (recall that ``k`` is bounded by ``n``).

Edge‑case handling mirrors the specification of ``DominatingSet``:

* ``k < 0`` – always unsatisfiable.  We return a formula containing a single
  empty clause ``[]``.
* ``k >= n`` – always satisfiable.  We return an empty formula (no clauses).
* ``n = 0`` – the above rules already give the correct answer.

The function ``reduce`` validates the source instance, builds the SAT instance
according to the rules above and returns it.
"""

from __future__ import annotations

from typing import List

from problems import DominatingSet, Sat


def _sequential_counter_clauses(n: int, k: int, var_offset: int) -> List[List[int]]:
    """Return clauses for the at‑most‑k cardinality constraint.

    ``var_offset`` is the number of original ``x_i`` variables; the auxiliary
    variable ``s[i][j]`` is mapped to ``var_offset + (i - 1) * k + j`` (1‑based
    ``i`` and ``j``).  The returned clauses use the integer variable numbers
    directly.
    """
    clauses: List[List[int]] = []

    def x(i: int) -> int:
        return i + 1  # original variables are 1..n

    def s(i: int, j: int) -> int:
        # i in 1..n, j in 1..k
        return var_offset + (i - 1) * k + j

    # 1. (¬x_i ∨ s_i_1) for each i
    for i in range(1, n + 1):
        clauses.append([-x(i - 1), s(i, 1)])

    # 2. (¬s_{i-1}_j ∨ s_i_j) for i>1, 1≤j≤k
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([-s(i - 1, j), s(i, j)])

    # 3. (¬x_i ∨ ¬s_{i-1}_{j-1} ∨ s_i_j) for i>1, 2≤j≤k
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-x(i - 1), -s(i - 1, j - 1), s(i, j)])

    # 4. Prevent more than k selections: (¬x_i ∨ ¬s_{i-1}_k) for i>1
    for i in range(2, n + 1):
        clauses.append([-x(i - 1), -s(i - 1, k)])

    # Base case: for j>1, s_1_j must be false because we cannot have ≥2 true among
    # the first vertex.  Encode as unit clauses ¬s_1_j.
    for j in range(2, k + 1):
        clauses.append([-s(1, j)])

    return clauses


def reduce(instance: dict) -> dict:
    """Reduce a Dominating‑Set instance to a SAT instance.

    The returned instance satisfies the SAT format used by ``problems.Sat``.
    """
    # Validate source instance (will raise if malformed)
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula – a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Always satisfiable – empty formula.
        return {"num_vars": n, "clauses": []}

    # Build adjacency list.
    neighbours: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)

    clauses: List[List[int]] = []

    # 1. Domination clauses: for each vertex v, at least one of v or its neighbours
    #    must be selected.
    for v in range(n):
        clause = [v + 1]  # x_v
        clause.extend([nbr + 1 for nbr in neighbours[v]])
        clauses.append(clause)

    # 2. Cardinality (at most k) using sequential counter.
    if k == 0:
        # Force all x_i false.
        for i in range(n):
            clauses.append([-(i + 1)])
    else:
        aux_offset = n  # variables 1..n are x_i, auxiliary start after them
        clauses.extend(_sequential_counter_clauses(n, k, aux_offset))

    num_vars = n + (0 if k == 0 else n * k)
    return {"num_vars": num_vars, "clauses": clauses}

