"""Reduction from Dominating Set to SAT.

We encode the existence of a dominating set of size at most k using a
standard encoding that introduces a variable for each ordered pair (vertex,
slot).  Variable y_{i,j} (SAT variable i*k + j, 1‑based) means that vertex i
is chosen as the j‑th element of the dominating set.  This encoding yields a
formula whose size is O(n·k^2) – polynomial in the input size.

Constraints:
1. A vertex can occupy at most one slot.
2. A slot can be occupied by at most one vertex.
3. Every graph vertex must be dominated, i.e., either it appears in some
   slot or one of its neighbours appears in some slot.

Edge cases are handled explicitly to keep the formula small.
"""

from __future__ import annotations

import itertools
from typing import Dict, List

from problems import DominatingSet, Sat, InvalidInstance


def _unsat_instance() -> Dict:
    """Return a trivially unsatisfiable SAT instance (contains an empty clause)."""
    return {"num_vars": 1, "clauses": [[]]}


def _sat_instance_trivial() -> Dict:
    """Return a trivially satisfiable SAT instance (single positive unit clause)."""
    return {"num_vars": 1, "clauses": [[1]]}


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating‑Set instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dict with keys "n", "edges" and "k" as defined by ``DominatingSet``.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases
    if k < 0:
        return _unsat_instance()
    if n == 0:
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        return _sat_instance_trivial()
    if k == 0:
        # Non‑empty graph cannot be dominated by an empty set.
        return _unsat_instance()

    # Build adjacency list
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Number of SAT variables = n * k (each vertex-slot pair)
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. A vertex appears in at most one slot.
    for i in range(n):
        for j1 in range(1, k + 1):
            for j2 in range(j1 + 1, k + 1):
                clauses.append([-(i * k + j1), -(i * k + j2)])

    # 2. Each slot holds at most one vertex.
    for j in range(1, k + 1):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                clauses.append([-(i1 * k + j), -(i2 * k + j)])

    # 3. Domination constraints: every vertex v must be dominated.
    for v in range(n):
        lits: List[int] = []
        # v itself in any slot
        for j in range(1, k + 1):
            lits.append(v * k + j)
        # any neighbour in any slot
        for u in adj[v]:
            for j in range(1, k + 1):
                lits.append(u * k + j)
        # Remove possible duplicates
        lits = list(dict.fromkeys(lits))
        clauses.append(lits)

    return {"num_vars": num_vars, "clauses": clauses}

