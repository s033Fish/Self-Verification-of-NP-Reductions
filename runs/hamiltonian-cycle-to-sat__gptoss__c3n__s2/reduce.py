"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected graph given by `{"n": n, "edges": [[u, v], ...]}`.
The target problem is a CNF formula `{"num_vars": m, "clauses": [[lit, ...], ...]}`.

We use the classic polynomial‑time reduction that introduces a Boolean
variable `x_{i,v}` (encoded as a positive integer) meaning *vertex `v` appears
at position `i` in the Hamiltonian cycle* (positions are 0‑based and there
are exactly `n` positions).  The reduction creates clauses that enforce:

1. **Exactly one vertex per position** – a clause containing all
   `x_{i,v}` for a fixed `i` forces at least one vertex, and pairwise
   negative clauses `¬x_{i,u} ∨ ¬x_{i,v}` forbid two different vertices
   sharing the same position.

2. **Each vertex appears exactly once** – analogous clauses for each
   vertex across all positions.

3. **Consecutive vertices must be joined by an edge** – for every position
   `i` and every non‑edge `{u, v}` we add `¬x_{i,u} ∨ ¬x_{i+1 mod n, v}`.
   This prevents the cycle from using a non‑existent edge.

If `n <= 2` the Hamiltonian‑Cycle instance is always a *no* instance.  We
return an unsatisfiable SAT instance consisting of a single empty clause.

The function runs in polynomial time in the size of the input graph and
conforms to the validation helpers defined in ``problems.py``.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to n*n (inclusive) as required by the
    SAT definition.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to an equivalent SAT instance.

    The returned instance satisfies ``Sat.validate`` and is satisfiable
    iff the input graph contains a Hamiltonian cycle.
    """
    # Validate the source instance first.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial no‑instances (n <= 2) map to an unsatisfiable formula.
    if n <= 2:
        # An empty clause [] makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Build a set of existing undirected edges for O(1) membership tests.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses: List[List[int]] = []

    # 1. Exactly one vertex per position.
    for i in range(n):
        # At least one vertex occupies position i.
        clauses.append([_var_index(i, v, n) for v in range(n)])
        # No two distinct vertices share the same position.
        for u, v in combinations(range(n), 2):
            clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 2. Each vertex appears exactly once.
    for v in range(n):
        # Vertex v appears somewhere.
        clauses.append([_var_index(i, v, n) for i in range(n)])
        # Vertex v cannot appear in two different positions.
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Consecutive positions must correspond to an edge.
    # For every i and every unordered pair {u, v} that is NOT an edge,
    # forbid having u at i and v at i+1 (mod n).
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-_var_index(i, u, n), -_var_index(nxt, v, n)])

    # Build the SAT instance dictionary.
    sat_instance: Dict[str, Any] = {"num_vars": n * n, "clauses": clauses}
    # Validate the target instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

