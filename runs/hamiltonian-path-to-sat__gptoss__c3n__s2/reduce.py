"""Reduction from Hamiltonian Path to SAT.

The reduction follows the classic encoding using a variable x_{i,v} that
means "vertex *v* appears at position *i* of the Hamiltonian path".

For a graph with *n* vertices we create *n·n* Boolean variables (indexed
from 1 as required by the SAT definition).  The CNF consists of:

1. **Exactly one vertex per position** – at least one vertex occupies each
   position and no two vertices occupy the same position.
2. **Exactly one position per vertex** – each vertex appears somewhere in the
   path and never twice.
3. **Adjacency constraints** – consecutive positions must correspond to an
   edge of the graph.  For every non‑edge {u, v} and every position i we add
   clauses forbidding (u at i ∧ v at i+1) and (v at i ∧ u at i+1).

Edge cases are handled explicitly:

* ``n == 0`` – the answer is always *no*.  We output an unsatisfiable formula
  (a single empty clause).
* ``n == 1`` – the answer is always *yes*.  An empty clause list (which is
  trivially satisfiable) suffices.

The function runs in polynomial time in the size of the input graph.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import HamiltonianPath, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1..n*n as required by the SAT format.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    The returned dictionary conforms to the ``Sat`` problem format:
    ``{"num_vars": m, "clauses": [[...], ...]}``.
    """
    # Validate source instance.
    HamiltonianPath.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case handling.
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable (no constraints needed).
        return {"num_vars": 1, "clauses": []}

    # Build a set of undirected edges for O(1) lookup.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: List[List[int]] = []
    m = n * n  # number of variables

    # 1. Exactly one vertex per position.
    for i in range(n):
        # At least one vertex at position i.
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)
        # At most one vertex: pairwise mutual exclusion.
        for u, v in combinations(range(n), 2):
            clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 2. Exactly one position per vertex.
    for v in range(n):
        # At least one position for vertex v.
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
        # At most one position: pairwise mutual exclusion.
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Adjacency constraints – forbid non‑edges on consecutive positions.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    # (u at i) AND (v at i+1) is forbidden.
                    clauses.append([-_var_index(i, u, n), -_var_index(i + 1, v, n)])
        # The loop above already covers both (u,v) and (v,u) because we iterate
        # over all ordered pairs u!=v.

    return {"num_vars": m, "clauses": clauses}

