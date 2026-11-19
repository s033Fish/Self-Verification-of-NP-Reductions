"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The reduction follows the classic encoding using variables
``x_{i,v}`` meaning *vertex ``v`` occupies position ``i`` in the Hamiltonian
cycle* (positions are 0‑based and there are exactly ``n`` positions for a graph
with ``n`` vertices).  The SAT formula enforces:

1. Every position contains exactly one vertex.
2. Every vertex appears in exactly one position.
3. Consecutive positions correspond to an edge of the input graph.

For ``n <= 2`` the Hamiltonian‑Cycle instance is always a NO‑instance.  The
formula ``[[]]`` (an empty clause) is unsatisfiable, so we return that directly
to avoid the degenerate case where the generic encoding would produce a
trivially satisfiable empty formula.

The function runs in polynomial time in the size of the input graph.
"""

from __future__ import annotations

from typing import List, Dict

# Import the problem classes only for type checking / documentation.  The
# reduction itself must not call any solver methods.
from problems import SOURCE, TARGET


def _var_index(i: int, v: int, n: int) -> int:
    """Map a pair (position, vertex) to a SAT variable number (1‑based).

    Variables are numbered ``1 .. n*n`` where ``n`` is the number of vertices.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dict with keys ``"n"`` and ``"edges"`` as described in the problem
        specification.

    Returns
    -------
    dict
        A SAT instance in the format ``{"num_vars": m, "clauses": [...]}``.
    """
    n = instance["n"]
    edges = instance["edges"]

    # Edge cases: n <= 2 are always NO.  Return an explicitly unsatisfiable
    # formula (a single empty clause).
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}

    # Build a set for constant‑time adjacency checks.  Because the graph is
    # undirected we store both (u, v) and (v, u).
    adjacency = set()
    for u, v in edges:
        adjacency.add((u, v))
        adjacency.add((v, u))

    clauses: List[List[int]] = []

    # 1. Every position i (0..n-1) contains at least one vertex.
    for i in range(n):
        clauses.append([_var_index(i, v, n) for v in range(n)])
        # At most one vertex per position.
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 2. Every vertex appears in exactly one position.
    for v in range(n):
        clauses.append([_var_index(i, v, n) for i in range(n)])
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Consecutive positions must correspond to an edge of the graph.
    #    For each position i and its successor (i+1) mod n we forbid any pair
    #    of non‑adjacent vertices.
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if (u, v) not in adjacency:
                    clauses.append([-_var_index(i, u, n), -_var_index(nxt, v, n)])

    return {"num_vars": n * n, "clauses": clauses}

