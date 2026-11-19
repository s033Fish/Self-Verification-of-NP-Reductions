"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The reduction follows the classic textbook encoding using a variable
``x_{i,v}`` that is true iff vertex ``v`` appears at position ``i`` in the
Hamiltonian path.  Positions are numbered ``0 .. n-1`` and vertices are also
``0 .. n-1``.  The SAT instance contains the following constraints:

1. **Exactly one vertex per position** – for each position ``i`` we add a
   clause asserting that *some* vertex occupies the position and for each
   pair of distinct vertices we add a clause forbidding them to both be at
   the same position.
2. **Exactly one position per vertex** – symmetric to (1).
3. **Adjacency** – for every pair of consecutive positions ``i`` and
   ``i+1`` we forbid assignments where the two vertices are not connected by
   an edge in the input graph.

The encoding is polynomial (``O(n^3)`` clauses) and works for all ``n >= 1``.
For the degenerate case ``n = 0`` the Hamiltonian‑Path problem is defined as
*no*; we therefore produce an unsatisfiable SAT instance consisting of a
single empty clause.  For ``n = 1`` the answer is always *yes*; an empty CNF
formula (no clauses) is trivially satisfiable, so we output that.

The public API is a single function ``reduce(instance)`` which receives a
Hamiltonian‑Path instance (as defined in ``problems.py``) and returns a SAT
instance in the required format.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import HamiltonianPath, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map the pair ``(position, vertex)`` to a 1‑based SAT variable.

    Variables are numbered from 1 to ``n * n`` in row‑major order:
    ``x_{0,0}`` → 1, ``x_{0,1}`` → 2, …, ``x_{n-1,n-1}`` → ``n*n``.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    The returned dictionary conforms to the ``Sat`` problem specification:
    ``{"num_vars": m, "clauses": [[...], ...]}``.
    """
    # Validate the source instance first – this will raise if malformed.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # Edge case handling for n = 0 and n = 1.
    if n == 0:
        # Unsatisfiable: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable: empty CNF.
        return {"num_vars": 1, "clauses": []}

    # Build adjacency set for O(1) edge existence checks.
    adj = {frozenset((u, v)) for u, v in edges}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i contains at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 1b. No position contains two different vertices.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 2. Each vertex appears in exactly one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Consecutive positions must correspond to an edge.
    # For every non‑edge (including self‑loops) we forbid it at consecutive slots.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v or frozenset((u, v)) not in adj:
                    # Not an edge → cannot be consecutive.
                    clauses.append([-_var_index(i, u, n), -_var_index(i + 1, v, n)])

    # Return the SAT instance.
    return {"num_vars": num_vars, "clauses": clauses}

