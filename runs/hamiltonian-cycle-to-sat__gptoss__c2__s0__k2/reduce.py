"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected Hamiltonian Cycle instance:
    {"n": n, "edges": [[u, v], ...]}
where vertices are 0..n-1 and edges are unordered pairs.

The target problem is SAT in CNF:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are integers where a positive value +v means variable v is true
and a negative value -v means variable v is false.

We encode the existence of a Hamiltonian cycle with the classic encoding
using position‑vertex variables x_{i,v} ("vertex v is at position i").
Positions i range from 0 to n-1 and vertices v from 0 to n-1.
Variable indices start at 1, so we map:
    var(i, v) = i * n + v + 1

The CNF consists of the following constraints (all standard for the
Hamiltonian‑cycle‑to‑SAT reduction):

1. **Each position contains at least one vertex**
   (x_{i,0} ∨ x_{i,1} ∨ … ∨ x_{i,n-1}) for every i.

2. **Each position contains at most one vertex**
   (¬x_{i,v} ∨ ¬x_{i,w}) for every i and every distinct v, w.

3. **Each vertex appears in at least one position**
   (x_{0,v} ∨ x_{1,v} ∨ … ∨ x_{n-1,v}) for every v.

4. **Each vertex appears in at most one position**
   (¬x_{i,v} ∨ ¬x_{j,v}) for every v and every distinct i, j.

5. **Consecutive positions must be adjacent in the graph**
   For every i (0 ≤ i < n) and for every pair of vertices (v, w)
   that are *not* connected by an edge, add the clause
   (¬x_{i,v} ∨ ¬x_{i+1 mod n,w}).

The construction runs in O(n^3) time, which is polynomial.

Edge cases:
* For n ≤ 2 the source instance is always a NO‑instance.  To reflect this
  we return a trivially unsatisfiable SAT formula – a single empty clause.
* The mapping works for any n ≥ 3.

The function ``reduce`` below follows the required signature and returns
the SAT instance as a dictionary compatible with the format described
in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Set, Tuple

def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position i and vertex v.

    Variables are numbered from 1 upwards as required by the SAT format.
    """
    return i * n + v + 1


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

    # Edge case: graphs with n <= 2 are always NO instances.
    if n <= 2:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for quick lookup of existing edges.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue  # ignore self‑loops, they are irrelevant for Hamiltonian cycles
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 3. Each vertex v appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex v appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 5. Edge constraints for consecutive positions.
    # For each position i and each non‑edge (v, w), forbid v at i and w at i+1.
    for i in range(n):
        next_i = (i + 1) % n
        for v in range(n):
            for w in range(n):
                if (v, w) not in adj:
                    clauses.append([-_var_index(i, v, n), -_var_index(next_i, w, n)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

