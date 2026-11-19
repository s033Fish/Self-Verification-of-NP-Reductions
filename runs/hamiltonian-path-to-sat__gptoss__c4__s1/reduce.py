"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The reduction follows the classic encoding using position variables:
    x_{i,v}  – vertex ``v`` occupies position ``i`` in the Hamiltonian path.
Variables are numbered from 1 upwards as required by the SAT problem
definition.

For a graph with ``n`` vertices we create ``n * n`` Boolean variables.
If ``n == 0`` the Hamiltonian Path instance is a definite *no*; we encode
this by a formula containing a single empty clause, which is unsatisfiable.
If ``n > 0`` we generate the following constraints (each expressed as a
list of integer literals):

1. **Each position contains at least one vertex** – a clause that is the
   disjunction of all ``x_{i,v}`` for a fixed ``i``.
2. **Each position contains at most one vertex** – for every pair of
   distinct vertices ``v`` and ``w`` we add ``¬x_{i,v} ∨ ¬x_{i,w}``.
3. **Each vertex appears in exactly one position** – analogous to (1) and
   (2) but swapping the roles of positions and vertices.
4. **Consecutive vertices must be adjacent** – for every non‑edge ``{u,v}``
   and every position ``i`` (0 ≤ i < n‑1) we forbid the assignment where ``u``
   is at ``i`` and ``v`` is at ``i+1`` (and vice‑versa) by adding the clause
   ``¬x_{i,u} ∨ ¬x_{i+1,v}`` and ``¬x_{i,v} ∨ ¬x_{i+1,u}``.

The produced instance conforms to the format defined in ``problems.py``:
``{"num_vars": m, "clauses": [[...], ...]}`` where literals are positive
for true and negative for false.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Set

from problems import HamiltonianPath, Sat


def _var_id(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to n*n inclusive.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    The function runs in polynomial time in the size of the input graph.
    """
    # Validate the source instance using the provided validator.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge set for quick lookup.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    # Special case n == 0 : always a NO instance. Encode unsatisfiable.
    if n == 0:
        # A formula with a single empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex (pairwise mutual exclusion).
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 3. Each vertex appears in exactly one position.
    for v in range(n):
        # At least once.
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)
        # At most once.
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 4. Non‑edges cannot be consecutive.
    # For every unordered pair {u, v} that is NOT an edge, forbid adjacency.
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                for i in range(n - 1):
                    # u at i, v at i+1 is forbidden
                    clauses.append([-_var_id(i, u, n), -_var_id(i + 1, v, n)])
                    # v at i, u at i+1 is forbidden
                    clauses.append([-_var_id(i, v, n), -_var_id(i + 1, u, n)])

    # Validate the produced SAT instance.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

