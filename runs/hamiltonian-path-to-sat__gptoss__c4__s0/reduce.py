"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`HamiltonianPath` (undirected Hamiltonian path
with arbitrary endpoints).  The target problem is :class:`Sat` (CNF
satisfiability).  This file implements a polynomial‑time many‑one reduction
``reduce`` that maps a Hamiltonian‑Path instance to a SAT instance that is
 satisfiable iff the original graph contains a Hamiltonian path.

The classic reduction introduces a Boolean variable ``X_{i,v}`` meaning
"vertex *v* occupies position *i* in the Hamiltonian path".  For a graph with
``n`` vertices we therefore have ``n * n`` variables, numbered from ``1`` to
``n*n`` (the SAT format expects variables to be 1‑based).  The constraints are:

1. **Each position contains exactly one vertex** – encoded by a clause that
   forces at least one vertex at each position and binary clauses forbidding
   two different vertices simultaneously at the same position.
2. **Each vertex appears exactly once** – analogous to (1) but across the
   positions.
3. **Consecutive vertices must be adjacent** – for every non‑edge ``{u,v}``
   and every consecutive position pair ``i,i+1`` we add the clause
   ``(~X_{i,u} ∨ ~X_{i+1,v})``.  This prevents the path from using a missing
   edge.

Edge‑cases are handled explicitly:

* ``n == 0`` – the answer is always *no*.  We return a SAT instance with an
  empty clause (unsatisfiable).
* ``n == 1`` – the answer is always *yes*.  The generic construction works, but
  we keep the implementation simple and let the generic clauses handle it.

The reduction runs in ``O(n^3)`` time – polynomial in the size of the input
graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, Sat


def _var_id(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` to a SAT variable id.

    Variables are numbered from 1 to n*n in row‑major order.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    The returned dictionary follows the format required by :class:`Sat`:
    ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges_input: List[List[int]] = instance["edges"]
    # Store edges as a set of unordered pairs for O(1) lookup.
    edges = {frozenset(e) for e in edges_input}

    # Edge case: n == 0 has no Hamiltonian path. Return an unsatisfiable SAT
    # instance (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # General case.
    m = n * n  # total number of Boolean variables
    clauses: List[List[int]] = []

    # 1. Each position i (0..n-1) contains at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 1b. No position contains two different vertices.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_id(i, u, n), -_var_id(i, v, n)])

    # 2. Each vertex v appears in at least one position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 2b. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 3. Consecutive vertices must be adjacent.
    # For every pair of consecutive positions i,i+1 and every non‑edge {u,v},
    # forbid u at i and v at i+1.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edges:
                    clauses.append([-_var_id(i, u, n), -_var_id(i + 1, v, n)])

    return {"num_vars": m, "clauses": clauses}

