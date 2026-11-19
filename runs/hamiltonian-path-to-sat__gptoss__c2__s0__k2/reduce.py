"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The source problem instance format (see ``problems.py``) is a dictionary:

    {"n": n, "edges": [[u, v], ...]}

where vertices are ``0..n-1`` and ``edges`` contains each undirected edge
exactly once.

The target SAT instance format is a dictionary:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1..m``.  A literal is an integer ``+v`` (meaning
variable ``v`` is true) or ``-v`` (meaning variable ``v`` is false).  An
empty clause (``[]``) is unsatisfiable; a formula with no clauses is
trivially satisfiable.

The reduction creates a classic encoding using variables
``X_{i,v}`` meaning *vertex* ``v`` occupies *position* ``i`` in the
Hamiltonian path (positions are ``0..n-1``).  There are ``n*n`` such
variables, numbered ``i * n + v + 1``.

Constraints encoded as CNF clauses:

1. **Each position contains at least one vertex** – a single clause per
   position with all variables for that position.
2. **Each position contains at most one vertex** – for each position and
   each unordered pair of distinct vertices ``v != w`` a clause
   ``(-X_{i,v} ∨ -X_{i,w})``.
3. **Each vertex appears in at least one position** – a clause per vertex
   containing all variables for that vertex across positions.
4. **Each vertex appears at most once** – for each vertex and each pair of
   distinct positions ``i != j`` a clause ``(-X_{i,v} ∨ -X_{j,v})``.
5. **Consecutive vertices must be adjacent** – for each position ``i``
   (except the last) and each unordered non‑edge ``{u, v}`` we forbid the
   ordering ``u`` at ``i`` followed by ``v`` at ``i+1`` and also the reverse
   ordering.  This yields two clauses per non‑edge per position:
   ``(-X_{i,u} ∨ -X_{i+1,v})`` and ``(-X_{i,v} ∨ -X_{i+1,u})``.

Edge cases required by the source definition are handled explicitly:

* ``n == 0`` – the answer is always *no*.  We output a formula containing a
  single empty clause, which is unsatisfiable.
* ``n == 1`` – the answer is always *yes*.  We output a formula with no
  clauses (satisfiable) and a single variable (the variable count is
  irrelevant for satisfiability).

The construction runs in polynomial time (O(n^3) in the worst case) and
produces a SAT instance that is satisfiable iff the original graph has a
Hamiltonian path.
"""

from typing import List, Dict, Any


def _var(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    Variables are numbered from 1 to n*n in row‑major order.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...]}``

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}``
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge‑case handling ---------------------------------------------------
    if n == 0:
        # No vertices → answer is always NO.  Return an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Single vertex → always YES.  Return a trivially satisfiable formula.
        return {"num_vars": 1, "clauses": []}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    clauses: List[List[int]] = []
    num_vars = n * n

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var(i, v, n), -_var(i, w, n)])

    # 3. Each vertex v appears in at least one position.
    for v in range(n):
        clause = [_var(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex v appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # 5. Edge constraints for consecutive positions.
    # For each position i (0 .. n-2) and each unordered pair (u, v) that is NOT an edge,
    # forbid u at i and v at i+1, and also v at i and u at i+1.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v or adj[u][v]:
                    continue
                # forbid (u at i) && (v at i+1)
                clauses.append([-_var(i, u, n), -_var(i + 1, v, n)])
                # forbid (v at i) && (u at i+1)
                clauses.append([-_var(i, v, n), -_var(i + 1, u, n)])

    return {"num_vars": num_vars, "clauses": clauses}

