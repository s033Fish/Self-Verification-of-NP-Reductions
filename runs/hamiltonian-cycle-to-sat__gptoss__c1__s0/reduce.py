"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected Hamiltonian Cycle instance:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.  The target is a CNF formula:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are integers: +v for variable v true, -v for false.

We use the classic polynomial‑time reduction that introduces a Boolean
variable x_{v,i} meaning "vertex *v* occupies position *i* in the
Hamiltonian cycle" (positions are 0..n-1).  There are n² variables.

Constraints encoded as clauses:
1. **Each position contains at least one vertex** – a clause that is the
   disjunction of all x_{v,i} for a fixed i.
2. **No position contains two different vertices** – for every i and for
   every pair v≠w, the clause (¬x_{v,i} ∨ ¬x_{w,i}).
3. **Each vertex appears in exactly one position** – analogous to (1) and
   (2) with the roles of vertices and positions swapped.
4. **Consecutive vertices must be connected by an edge** – for every i
   and for every ordered pair (v,w) that is *not* an edge, we add the clause
   (¬x_{v,i} ∨ ¬x_{w, (i+1) mod n}).

If n ≤ 2 the source instance is always a NO‑instance.  In that case we
return an obviously unsatisfiable SAT instance consisting of a single
empty clause.

The function ``reduce`` performs this construction and returns a dictionary
compatible with the SAT definition in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Set


def _var_id(v: int, i: int, n: int) -> int:
    """Map (vertex, position) to a SAT variable number (1‑based)."""
    # Variables are numbered 1..n*n in row‑major order.
    return v * n + i + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...]}``

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[literal, ...], ...]}``
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: n <= 2 – always NO. Return an unsatisfiable formula.
    if n <= 2:
        # Need at least one variable; use variable 1 with an empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build a set of undirected edges for O(1) lookup.
    edge_set: Set[frozenset] = {frozenset(e) for e in edges}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_id(v, i, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position i contains two different vertices.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(v, i, n), -_var_id(w, i, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_id(v, i, n) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(v, i, n), -_var_id(v, j, n)])

    # 5. Edge constraints: if (v,w) is NOT an edge, they cannot be consecutive.
    for i in range(n):
        next_i = (i + 1) % n
        for v in range(n):
            for w in range(n):
                if v == w:
                    continue
                if frozenset((v, w)) not in edge_set:
                    # ordered pair (v at i, w at next_i) is forbidden
                    clauses.append([-_var_id(v, i, n), -_var_id(w, next_i, n)])

    return {"num_vars": num_vars, "clauses": clauses}

