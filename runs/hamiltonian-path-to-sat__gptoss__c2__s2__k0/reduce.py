"""Reduction from Hamiltonian Path to SAT.

The source problem is the undirected Hamiltonian Path problem (any endpoints).
Instance format (as defined in ``problems.py``)::

    {"n": n, "edges": [[u, v], ...]}

where vertices are ``0..n-1`` and each edge is an unordered pair ``[u, v]``.

The target problem is CNF SAT.  Instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Literals are represented as ``+v`` for a positive occurrence of variable ``v``
and ``-v`` for a negated occurrence.  Variables are numbered from ``1`` to
``m``.

The reduction creates a variable ``x_{i,v}`` (encoded as a single integer) that
stands for “vertex *v* occupies position *i* in the Hamiltonian path”.  For a
graph with ``n`` vertices we therefore have ``n * n`` variables, numbered
``1`` … ``n*n`` using the mapping ``var(i, v) = i * n + v + 1``.

Constraints encoded as clauses:

1. **Each position contains exactly one vertex** – a clause with all positive
   literals for a given position ensures *at least* one vertex, and pairwise
   negative clauses forbid two vertices sharing the same position.
2. **Each vertex appears in exactly one position** – analogous to (1) but over
   positions for a fixed vertex.
3. **Consecutive vertices must be adjacent** – for every pair of positions
   ``i`` and ``i+1`` and for every unordered non‑edge ``{u, v}`` we add the clause
   ``¬x_{i,u} ∨ ¬x_{i+1,v}``.  This forbids placing non‑adjacent vertices next to
   each other in the path.  The clause also handles the case ``u == v`` which
   prevents the same vertex from appearing consecutively (already excluded by
   (2) but harmless to include).

Edge cases are handled explicitly:

* ``n == 0`` – the Hamiltonian Path problem is a definite *no*, so we output an
  unsatisfiable SAT instance consisting of a single empty clause.
* ``n == 1`` – the answer is always *yes*; we output a trivially satisfiable
  instance (no clauses) with a single dummy variable.

The function runs in polynomial time (O(n³) clauses) and does not invoke any
solver.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian Path instance to an equivalent SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": [[u, v], ...]}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": [[literal, ...], ...]}``
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case n == 0 : always NO -> produce unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}  # empty clause makes formula UNSAT

    # Edge case n == 1 : always YES -> trivially satisfiable formula.
    if n == 1:
        return {"num_vars": 1, "clauses": []}

    # Build a set of undirected edges for O(1) adjacency checks.
    edge_set = {frozenset((u, v)) for u, v in edges}

    # Helper to map (position i, vertex v) to a SAT variable number (1‑based).
    def var(i: int, v: int) -> int:
        return i * n + v + 1

    clauses: List[List[int]] = []

    # 1. Each position i contains exactly one vertex.
    for i in range(n):
        # At least one vertex in position i.
        clauses.append([var(i, v) for v in range(n)])
        # No two different vertices occupy the same position.
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 2. Each vertex v appears in exactly one position.
    for v in range(n):
        # At least one position for vertex v.
        clauses.append([var(i, v) for i in range(n)])
        # Vertex v cannot be in two different positions.
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # 3. Consecutive positions must correspond to an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if frozenset((u, v)) not in edge_set:
                    # forbid u at position i and v at position i+1
                    clauses.append([-var(i, u), -var(i + 1, v)])

    return {"num_vars": n * n, "clauses": clauses}

