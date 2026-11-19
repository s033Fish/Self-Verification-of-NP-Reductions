"""Reduction from Dominating Set to SAT.

The source problem is :class:`DominatingSet` defined in ``problems.py``.
The target problem is :class:`Sat`.

We implement a polynomial‑time reduction using the sequential counter
encoding (Sinz 2005) to enforce the cardinality bound |D| ≤ k.  The
reduction creates one Boolean variable x_i for each vertex i (1‑based) and
auxiliary variables s_{i,j} to count how many of the first i vertices are
selected.  The resulting CNF size is O(n·k).
"""

from __future__ import annotations

import itertools
from typing import Dict, List

from problems import DominatingSet, Sat, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating‑Set instance to a SAT instance.

    Parameters
    ----------
    instance: dict with keys "n", "edges", "k".

    Returns
    -------
    dict representing a SAT instance.
    """
    DominatingSet.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases
    if k < 0:
        # Unsatisfiable formula (empty clause)
        return {"num_vars": 1, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses: List[List[int]] = []

    # Domination clauses: each vertex or a neighbor must be chosen
    for v in range(n):
        lits = [v + 1]
        for nb in adj[v]:
            lits.append(nb + 1)
        clauses.append(lits)

    # Cardinality constraint: at most k vertices selected
    if k >= n:
        # No restriction needed
        pass
    elif k == 0:
        # Force all x_i false
        for i in range(1, n + 1):
            clauses.append([-i])
    else:
        # Sequential counter encoding
        # auxiliary variable s_{i,j} (i=1..n, j=1..k) -> fresh var number
        def aux(i: int, j: int) -> int:
            return n + (i - 1) * k + j

        # 1) (¬x_i ∨ s_{i,1}) for each i
        for i in range(1, n + 1):
            clauses.append([-i, aux(i, 1)])

        # 2) (¬s_{i-1,j} ∨ s_{i,j}) for i=2..n, j=1..k
        for i in range(2, n + 1):
            for j in range(1, k + 1):
                clauses.append([-aux(i - 1, j), aux(i, j)])

        # 3) (¬x_i ∨ ¬s_{i-1,j-1} ∨ s_{i,j}) for i=2..n, j=2..k
        for i in range(2, n + 1):
            for j in range(2, k + 1):
                clauses.append([-i, -aux(i - 1, j - 1), aux(i, j)])

        # 4) (¬x_i ∨ ¬s_{i-1,k}) for i=2..n to forbid >k selections
        for i in range(2, n + 1):
            clauses.append([-i, -aux(i - 1, k)])

    # Total number of variables includes auxiliaries if any were added
    total_vars = n
    if k > 0 and k < n:
        total_vars = n + n * k  # each i has k auxiliaries
    return {"num_vars": total_vars, "clauses": clauses}

