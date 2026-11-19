"""Reduction from Hamiltonian Cycle to SAT.

The source problem is :class:`HamiltonianCycle` defined in ``problems.py``.
The target problem is :class:`Sat` also defined there.

We implement the classic polynomial‑time reduction using variables
``x_{i,v}`` meaning *vertex* ``v`` occupies *position* ``i`` in the
Hamiltonian cycle (positions are taken modulo ``n``).  The reduction
produces a CNF formula that is satisfiable iff the graph has a Hamiltonian
cycle.

The reduction follows the textbook construction:

* **Exactly one vertex per position** – at least one (a long clause) and
  at most one (pairwise negative clauses).
* **Exactly one position per vertex** – analogous constraints.
* **Adjacency constraints** – for each ordered pair of non‑adjacent
  vertices ``(u, v)`` and each position ``i`` we add the clause
  ``¬x_{i,u} ∨ ¬x_{i+1,v}``.  This forbids a non‑edge from appearing as two
  consecutive vertices on the cycle.

Edge cases:

* For ``n <= 2`` a Hamiltonian cycle does not exist, so we return an
  unsatisfiable formula – a single empty clause.
* For ``n == 3`` the construction works correctly; the triangle graph
  yields a satisfiable formula.

The function ``reduce`` validates the source instance, builds the CNF and
returns it as a plain dictionary compatible with the ``Sat`` problem
definition.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any, Set

from problems import HamiltonianCycle, Sat


def _edge_set(edges: List[List[int]]) -> Set[frozenset[int]]:
    """Return a set of undirected edges represented as frozensets.

    ``edges`` is a list of ``[u, v]`` where ``u != v``.  The function
    normalises each edge to ``frozenset({u, v})`` for O(1) adjacency
    queries.
    """

    return {frozenset(e) for e in edges}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dict following the format of :class:`HamiltonianCycle` – keys
        ``"n"`` and ``"edges"``.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """

    # Validate the source instance first – this raises InvalidInstance on
    # malformed input, matching the contract of the problems module.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial unsatisfiable case for n <= 2.
    if n <= 2:
        # Zero variables and a single empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Mapping (position, vertex) -> SAT variable id (1‑based).
    # Variable ids are contiguous from 1 to n*n.
    def var_id(pos: int, vertex: int) -> int:
        return pos * n + vertex + 1

    edge_set = _edge_set(edges)
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [var_id(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No position i contains two different vertices (pairwise negative).
    for i in range(n):
        for u, v in combinations(range(n), 2):
            clauses.append([-var_id(i, u), -var_id(i, v)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [var_id(i, v) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two different positions.
    for v in range(n):
        for i, j in combinations(range(n), 2):
            clauses.append([-var_id(i, v), -var_id(j, v)])

    # 5. Edge constraints: forbid consecutive positions using a non‑edge.
    # For each ordered pair (u, v) that is NOT an edge, and for each i,
    # add (¬x_{i,u} ∨ ¬x_{i+1,v}).  The graph is undirected, so we also
    # forbid the opposite direction implicitly by iterating over all ordered
    # pairs.
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-var_id(i, u), -var_id(nxt, v)])

    num_vars = n * n
    # Validate the produced SAT instance before returning.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

