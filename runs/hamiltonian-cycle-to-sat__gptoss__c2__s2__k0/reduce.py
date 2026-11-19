"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected Hamiltonian Cycle instance represented as
```
{"n": n, "edges": [[u, v], ...]}
```
where vertices are numbered 0 … n‑1.

The target problem is SAT in CNF form represented as
```
{"num_vars": m, "clauses": [[literal, ...], ...]}
```
Variables are numbered 1 … m and a literal is an integer: a positive value
``+v`` encodes the variable *v* being true, a negative value ``-v`` encodes the
variable being false.

The classic polynomial‑time reduction introduces a Boolean variable
``X_{i,v}`` meaning *vertex* ``v`` occupies *position* ``i`` (positions are 0 …
``n-1``) in the Hamiltonian cycle.  There are ``n²`` variables.

Constraints encoded as clauses:

1. **Exactly one vertex per position** – for each position ``i`` we add a clause
   requiring at least one vertex:
   ``X_{i,0} ∨ X_{i,1} ∨ … ∨ X_{i,n-1}``.  To enforce *at most one* we add pairwise
   negative clauses ``¬X_{i,u} ∨ ¬X_{i,v}`` for every ``u < v``.

2. **Exactly one position per vertex** – for each vertex ``v`` we add a clause
   ``X_{0,v} ∨ X_{1,v} ∨ … ∨ X_{n-1,v}`` and pairwise negative clauses ``¬X_{i,v}
   ∨ ¬X_{j,v}`` for ``i < j``.

3. **Edges must exist between consecutive positions** – for each position ``i``
   (with ``i+1`` taken modulo ``n``) and for each unordered pair of distinct
   vertices ``(u, w)`` that is *not* an edge in the input graph we forbid the
   assignment ``X_{i,u}`` and ``X_{i+1,w}`` simultaneously by adding the clause
   ``¬X_{i,u} ∨ ¬X_{i+1,w}``.  This also handles the wrap‑around from the last
   position back to the first.

If ``n <= 2`` the Hamiltonian Cycle problem is defined to be a *no* instance.
In that case we output a trivially unsatisfiable formula – a single empty clause
``[]`` – which the SAT definition marks as unsatisfiable.

The function ``reduce`` follows the interface required by the evaluation
framework: it receives a source instance dictionary and returns a target
instance dictionary.
"""

from __future__ import annotations

from typing import List, Dict, Set, Tuple

def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for ``X_{i,v}``.

    Variables are numbered from 1 to ``n*n`` in row‑major order:
    ``i`` iterates over positions and ``v`` over vertices.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": [[u, v], ...]}``

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}``
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: n <= 2 -> always NO. Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}  # empty clause makes formula false

    # Build adjacency set for O(1) edge queries.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue  # ignore loops, they are irrelevant for Hamiltonian cycles
        a, b = (u, v) if u < v else (v, u)
        adj.add((a, b))

    clauses: List[List[int]] = []
    m = n * n  # total variables

    # 1. Exactly one vertex per position
    for i in range(n):
        # At least one vertex in position i
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)
        # At most one vertex: pairwise negative clauses
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 2. Exactly one position per vertex
    for v in range(n):
        # At least one position for vertex v
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
        # At most one position: pairwise negative
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Edge constraints for consecutive positions
    for i in range(n):
        next_i = (i + 1) % n
        for u in range(n):
            for w in range(n):
                if u == w:
                    # a Hamiltonian cycle cannot stay on the same vertex
                    # between consecutive positions, but this is already
                    # prohibited by the "exactly one" constraints.
                    continue
                a, b = (u, w) if u < w else (w, u)
                if (a, b) not in adj:
                    clauses.append([-_var_index(i, u, n), -_var_index(next_i, w, n)])

    return {"num_vars": m, "clauses": clauses}

