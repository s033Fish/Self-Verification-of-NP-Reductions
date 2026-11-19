"""Reduction from Hamiltonian Cycle to SAT.

The source problem is the undirected Hamiltonian Cycle defined in
``problems.HamiltonianCycle``.  The target problem is generic CNF SAT
defined in ``problems.Sat``.

For a graph G = (V, E) with |V| = n we introduce Boolean variables
``x_{i,v}`` meaning *vertex v is the i‑th vertex on the Hamiltonian
cycle* (positions are taken modulo n).  The standard polynomial‑time
encoding uses the following constraints, each expressed as a set of
clauses:

1. **Each position contains exactly one vertex** – a clause that at
   least one vertex occupies the position and pairwise mutual exclusion
   clauses to forbid two vertices at the same position.
2. **Each vertex appears exactly once** – analogous to (1) but swapping
   the roles of positions and vertices.
3. **Consecutive vertices must be adjacent** – for every position i and
   for every non‑edge {u, v} we add a clause forbidding u at i and v at
   i+1 (mod n).

If ``n <= 2`` the Hamiltonian‑cycle instance is always a NO‑instance.
We therefore output an obviously unsatisfiable SAT formula – a single
empty clause.

The reduction runs in O(n^3) time, which is polynomial in the size of
the input graph.  The produced SAT instance uses ``n*n`` variables, one
for each ordered pair (position, vertex).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat


def _var_id(i: int, v: int, n: int) -> int:
    """Map (position i, vertex v) to a SAT variable number in 1..n*n.

    Variables are numbered row‑major: first all vertices for position 0,
    then for position 1, and so on.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where each literal
    is an integer ``+v`` (positive) for the variable being true or ``-v``
    for it being false.
    """
    # Validate the source instance using the provided class method.
    HamiltonianCycle.validate(instance)
    n: int = instance["n"]

    # Edge case: n <= 2 -> always NO. Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}  # empty clause = unsat

    edges = {frozenset(e) for e in instance["edges"]}

    clauses: List[List[int]] = []
    num_vars = n * n

    # 1. Each position i has exactly one vertex.
    for i in range(n):
        # At least one vertex at position i
        clauses.append([_var_id(i, v, n) for v in range(n)])
        # At most one vertex: pairwise mutual exclusion
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 2. Each vertex v appears in exactly one position.
    for v in range(n):
        # At least one position for vertex v
        clauses.append([_var_id(i, v, n) for i in range(n)])
        # At most one position: pairwise exclusion
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 3. Consecutive vertices must be adjacent.
    # For every position i and every unordered pair {u, v} that is NOT an edge,
    # forbid u at i and v at i+1 (mod n).
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edges:
                    # forbid (u at i) ∧ (v at i+1)
                    clauses.append([-_var_id(i, u, n), -_var_id(nxt, v, n)])

    # Assemble the SAT instance.
    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced instance (optional but good sanity check).
    Sat.validate(sat_instance)
    return sat_instance

