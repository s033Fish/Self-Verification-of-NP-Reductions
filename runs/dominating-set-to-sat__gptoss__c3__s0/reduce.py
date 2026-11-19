"""Reduction from Dominating Set to SAT.

The source problem is :class:`problems.DominatingSet` and the target is
``Sat``.  The reduction encodes a dominating set of size at most ``k`` using
``k`` *slots*.  Each slot can hold at most one vertex and each vertex can be
placed in at most one slot, which together enforce that at most ``k`` vertices
are selected.

For every vertex ``v`` we add a clause that requires at least one selected
vertex (in any slot) to be either ``v`` itself or a neighbour of ``v`` – this
guarantees domination.

The construction is polynomial in ``n`` (the number of vertices) and ``k``.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem definitions from the bundled ``problems.py``.
from problems import DominatingSet, Sat


def _var_index(slot: int, vertex: int, n: int) -> int:
    """Return the SAT variable number for placing *vertex* in *slot*.

    Variables are numbered starting from 1 as required by the SAT spec.
    ``slot`` is 0‑based and ``vertex`` is 0‑based.
    """
    return slot * n + vertex + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating‑Set instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}``.
    """
    # Validate the source instance – this will raise if malformed.
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases that can be handled without constructing a large formula.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated; a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # No vertices may be selected, but the graph is non‑empty → unsat.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency list for domination constraints.
    adjacency: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)

    clauses: List[List[int]] = []

    # 1. At most one vertex per slot.
    for slot in range(k):
        for i in range(n):
            vi = _var_index(slot, i, n)
            for j in range(i + 1, n):
                vj = _var_index(slot, j, n)
                clauses.append([-vi, -vj])

    # 2. Each vertex appears in at most one slot.
    for vertex in range(n):
        for slot1 in range(k):
            v1 = _var_index(slot1, vertex, n)
            for slot2 in range(slot1 + 1, k):
                v2 = _var_index(slot2, vertex, n)
                clauses.append([-v1, -v2])

    # 3. Domination clauses: for each vertex, at least one selected vertex
    #    (in any slot) is either the vertex itself or one of its neighbours.
    for v in range(n):
        clause: List[int] = []
        # vertex itself
        for slot in range(k):
            clause.append(_var_index(slot, v, n))
        # neighbours
        for nb in adjacency[v]:
            for slot in range(k):
                clause.append(_var_index(slot, nb, n))
        # The clause is guaranteed to be non‑empty because k > 0.
        clauses.append(clause)

    num_vars = n * k
    return {"num_vars": num_vars, "clauses": clauses}

