"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The reduction follows the classic textbook construction using a variable
``x_{i,v}`` meaning *vertex ``v`` occupies position ``i`` in the Hamiltonian
cycle* (positions are 0‑based and the cycle wraps around).  For a graph with
``n`` vertices we create ``n * n`` Boolean variables, numbered from 1 to
``n*n`` as required by the SAT instance format.

Constraints encoded as CNF clauses:

1. **Each position contains exactly one vertex**
   - At least one vertex in each position: a clause with all ``x_{i,v}``
     for fixed ``i``.
   - At most one vertex: for every pair ``v != w`` a clause
     ``(-x_{i,v} ∨ -x_{i,w})``.

2. **Each vertex appears in exactly one position**
   - At least one position for each vertex: a clause with all ``x_{i,v}``
     for fixed ``v``.
   - At most one position: for every pair ``i != j`` a clause
     ``(-x_{i,v} ∨ -x_{j,v})``.

3. **Consecutive vertices must be adjacent**
   For every position ``i`` (with ``next = (i+1) mod n``) and for every *non*
   edge ``(u, v)`` we add the clause ``(-x_{i,u} ∨ -x_{next,v})``.  Because the
   graph is undirected we consider ordered pairs; the clause for ``(v, u)``
   is added when the ordered pair is processed.

Edge cases:
* For ``n <= 2`` the Hamiltonian‑Cycle instance is always a *no* instance.
  We therefore output an unsatisfiable SAT formula – a single empty clause
  ``[]`` – which is never satisfied.

The function ``reduce(instance)`` validates the input, builds the clause set
according to the rules above, and returns a dictionary conforming to the
``Sat`` problem specification.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple

from problems import HamiltonianCycle, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to n*n in row‑major order:
    ``index = i * n + v + 1``.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as defined by
        :class:`HamiltonianCycle`.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate source instance
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # Edge case: n <= 2 -> always unsatisfiable
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}  # empty clause = unsat

    # Build adjacency set for quick lookup of existing edges
    adj = {frozenset((u, v)) for u, v in edges}

    m = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has exactly one vertex
    for i in range(n):
        # at least one vertex
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)
        # at most one vertex (pairwise)
        for v, w in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 2. Each vertex appears in exactly one position
    for v in range(n):
        # at least one position
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
        # at most one position (pairwise)
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Consecutive vertices must be adjacent (use non‑edges)
    # Pre‑compute all unordered non‑edges
    all_pairs = {frozenset((u, v)) for u in range(n) for v in range(n) if u != v}
    non_edges = all_pairs - adj
    for i in range(n):
        nxt = (i + 1) % n
        for pair in non_edges:
            u, v = tuple(pair)
            # clause forbids u at i and v at nxt
            clauses.append([-_var_index(i, u, n), -_var_index(nxt, v, n)])
            # also forbid v at i and u at nxt (the ordered counterpart)
            clauses.append([-_var_index(i, v, n), -_var_index(nxt, u, n)])

    # Validate target instance before returning
    Sat.validate({"num_vars": m, "clauses": clauses})
    return {"num_vars": m, "clauses": clauses}

