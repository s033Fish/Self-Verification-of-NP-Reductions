"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The source problem instance is a dictionary with keys:
    - "n": number of vertices (vertices are 0..n-1)
    - "edges": list of [u, v] pairs representing undirected edges.

The target problem (SAT) expects a dictionary:
    - "num_vars": total number of Boolean variables (numbered 1..m)
    - "clauses": list of clauses, each a list of integer literals.

We implement the classic polynomial‑time reduction using variables
``x_{v,i}`` meaning "vertex *v* occupies position *i* in the Hamiltonian
cycle" (positions are 0..n-1).  The reduction creates the following
constraints, each encoded as CNF clauses:

1. **Each position is occupied by exactly one vertex**
   - At least one vertex:  (x_{0,i} ∨ x_{1,i} ∨ … ∨ x_{n-1,i})
   - At most one vertex: for all v≠w, (¬x_{v,i} ∨ ¬x_{w,i})

2. **Each vertex appears in exactly one position**
   - At least one position: (x_{v,0} ∨ x_{v,1} ∨ … ∨ x_{v,n-1})
   - At most one position: for all i≠j, (¬x_{v,i} ∨ ¬x_{v,j})

3. **Consecutive positions must correspond to an edge**
   For every pair of vertices (u, v) that is *not* an edge, and for every
   position i, we add the clause (¬x_{u,i} ∨ ¬x_{v,i+1}) where i+1 is taken
   modulo n.  This forbids a non‑edge from being used consecutively in the
   cycle.

If ``n`` is 0, 1 or 2 the source instance is always a NO‑instance.  In that
case we output a trivially unsatisfiable SAT instance – a formula that
contains a single empty clause.

The reduction runs in O(n³) time, which is polynomial in the size of the
input graph.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

def _var_index(v: int, i: int, n: int) -> int:
    """Map (vertex, position) to a SAT variable number (1‑based).

    Variables are numbered consecutively: first all positions for vertex 0,
    then for vertex 1, and so on.
    """
    return v * n + i + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    The returned dictionary follows the format required by the ``Sat``
    problem class defined in ``problems.py``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge cases where the answer is always NO.
    if n <= 2:
        # An empty clause makes the formula unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # Build a set of existing undirected edges for O(1) look‑up.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue  # ignore loops, they are irrelevant for Hamiltonian cycles
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    clauses: List[List[int]] = []
    m = n * n  # total number of variables

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(v, i, n) for v in range(n)]
        clauses.append(clause)

    # 1b. No two vertices occupy the same position.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(v, i, n), -_var_index(w, i, n)])

    # 2. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_index(v, i, n) for i in range(n)]
        clauses.append(clause)

    # 2b. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(v, i, n), -_var_index(v, j, n)])

    # 3. Edge constraints: forbid consecutive non‑edges.
    # For each unordered non‑edge (u, v) and each position i, add (¬x_{u,i} ∨ ¬x_{v,i+1}).
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) in edge_set:
                continue  # there is an edge, no restriction needed
            for i in range(n):
                j = (i + 1) % n
                clauses.append([-_var_index(u, i, n), -_var_index(v, j, n)])
                clauses.append([-_var_index(v, i, n), -_var_index(u, j, n)])

    return {"num_vars": m, "clauses": clauses}

