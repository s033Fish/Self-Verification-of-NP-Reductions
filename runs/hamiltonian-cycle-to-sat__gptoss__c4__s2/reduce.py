"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The reduction follows the classic encoding using variables
``x_{v,i}`` meaning "vertex *v* is at position *i* in the Hamiltonian
cycle" where positions are taken modulo *n*.

For a graph with ``n`` vertices we create ``n * n`` Boolean variables
numbered from 1 to ``n*n`` (the SAT format expects variables numbered
starting at 1).  The mapping is:

    var(v, i) = v * n + i + 1   # 0‑based ``v`` and ``i``

The CNF consists of the following constraints:

1. **Each position contains at least one vertex**
   ``(x_{0,i} ∨ x_{1,i} ∨ … ∨ x_{n‑1,i})`` for every ``i``.
2. **Each position contains at most one vertex**
   ``(¬x_{u,i} ∨ ¬x_{v,i})`` for all ``u < v`` and each ``i``.
3. **Each vertex appears in at least one position**
   ``(x_{v,0} ∨ x_{v,1} ∨ … ∨ x_{v,n‑1})`` for every ``v``.
4. **Each vertex appears in at most one position**
   ``(¬x_{v,i} ∨ ¬x_{v,j})`` for all ``i < j``.
5. **Adjacency constraints** – if ``{u, v}`` is *not* an edge, then
   ``u`` cannot be followed by ``v`` in the cycle and vice‑versa:
   ``(¬x_{u,i} ∨ ¬x_{v,i+1})`` for every ``i`` (indices modulo ``n``).

For the trivial cases ``n <= 2`` the source problem is always a *no*
instance.  We therefore output an unsatisfiable SAT instance – a formula
containing a single empty clause ``[]``.

The function ``reduce`` validates the input, builds the clause list as
described and returns a dictionary compatible with the ``Sat`` problem
definition.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

from problems import HamiltonianCycle, Sat, InvalidInstance


def _var(v: int, i: int, n: int) -> int:
    """Return the SAT variable number for vertex ``v`` at position ``i``.

    Variables are 1‑based as required by the SAT definition.
    """
    return v * n + i + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    The returned instance satisfies the SAT format and is satisfiable
    iff the input graph has a Hamiltonian cycle.
    """
    # Validate source instance first – will raise InvalidInstance on error.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial no‑instances (n <= 2).  Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for O(1) edge checks.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var(v, i, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(u, i, n), -_var(v, i, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var(v, i, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # 5. Non‑edge adjacency constraints.
    # For every ordered pair (u, v) that is NOT an edge, forbid u at i and v at i+1.
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if (u, v) not in adj:
                    clauses.append([-_var(u, i, n), -_var(v, nxt, n)])

    # The number of variables is n * n.
    sat_instance: Dict[str, Any] = {"num_vars": n * n, "clauses": clauses}

    # Validate the produced SAT instance (helps catch bugs).
    Sat.validate(sat_instance)
    return sat_instance

