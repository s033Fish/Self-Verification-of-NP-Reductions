"""Reduction from Vertex Cover to SAT.

The source problem is defined in ``problems.py`` as ``VertexCover`` with
instances of the form ``{"n": n, "edges": [[u, v], ...], "k": k}``.
The target problem is ``Sat`` with instances ``{"num_vars": m,
"clauses": [[literal, ...], ...]}``.  Literals are represented by signed
integers: a positive integer ``v`` stands for the literal *v* (variable ``v``
is true) and a negative integer ``-v`` stands for the literal *¬v*.

We implement the classic polynomial‑time many‑one reduction that encodes the
question "does the graph have a vertex cover of size at most *k*?" as a SAT
formula that is satisfiable iff the answer is *yes*.

If ``k`` is negative the answer is always *no* – we return an unsatisfiable
formula (a single empty clause).  If ``k`` is at least ``n`` the answer is
always *yes* – we return a trivially satisfiable formula consisting of a
single unit clause.  The same trivial formula is used when the graph contains
no edges.

For the non‑trivial case (``0 ≤ k < n`` and at least one edge) we create a
boolean variable ``x_{i,j}`` for each vertex ``i`` (0‑based) and each position
``j`` in the cover (1‑based, ``1 … k``).  The variable is true exactly when
vertex ``i`` occupies position ``j`` in the chosen cover.  The encoding uses
four families of clauses:

1. **Every position is occupied** – for each ``j`` a clause containing all
   ``x_{i,j}`` (positive literals).
2. **At most one vertex per position** – for each ``j`` and each distinct pair
   ``i < i'`` a clause ``¬x_{i,j} ∨ ¬x_{i',j}``.
3. **A vertex cannot appear in two positions** – for each vertex ``i`` and
   each distinct pair ``j < j'`` a clause ``¬x_{i,j} ∨ ¬x_{i,j'}``.
4. **Edge coverage** – for each edge ``(u, v)`` a clause that asserts that at
   least one endpoint appears in *some* position: ``x_{u,1} ∨ … ∨ x_{u,k} ∨
   x_{v,1} ∨ … ∨ x_{v,k}``.

These clauses are polynomial in the size of the input (``O(n·k^2 + |E|·k)``).
If the original instance has a vertex cover of size ≤ k, we can extend it to
exactly ``k`` distinct vertices (by arbitrarily adding unused vertices) and
obtain a satisfying assignment.  Conversely, any satisfying assignment selects
exactly ``k`` distinct vertices that cover every edge, yielding a vertex cover
of size ≤ k.

The ``reduce`` function follows the specification required by the evaluation
framework: it receives a source instance (a ``dict``) and returns a target
instance (also a ``dict``).  No external solvers are invoked, and the runtime
is polynomial.
"""

from __future__ import annotations

from typing import Dict, List

def _var_index(i: int, j: int, n: int, k: int) -> int:
    """Map vertex ``i`` (0‑based) and position ``j`` (1‑based) to a SAT variable.

    Variables are numbered from ``1`` to ``n*k``.  The formula uses a flat
    indexing ``(i * k + (j-1) + 1)``.
    """
    return i * k + (j - 1) + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": List[List[int]], "k": int}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}``
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if k >= n:
        # Always satisfiable – single unit clause.
        return {"num_vars": 1, "clauses": [[1]]}
    if not edges:
        # No edges -> trivially satisfiable.
        return {"num_vars": 1, "clauses": [[1]]}

    # General case: build the encoding.
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Every position j must be occupied by at least one vertex.
    for j in range(1, k + 1):
        clause = [_var_index(i, j, n, k) for i in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position (pairwise mutual exclusion).
    for j in range(1, k + 1):
        for i in range(n):
            vi = _var_index(i, j, n, k)
            for ip in range(i + 1, n):
                vip = _var_index(ip, j, n, k)
                clauses.append([-vi, -vip])

    # 3. A vertex cannot occupy two different positions.
    for i in range(n):
        for j in range(1, k + 1):
            v = _var_index(i, j, n, k)
            for jp in range(j + 1, k + 1):
                vp = _var_index(i, jp, n, k)
                clauses.append([-v, -vp])

    # 4. Edge coverage clauses.
    for (u, v) in edges:
        clause: List[int] = []
        for j in range(1, k + 1):
            clause.append(_var_index(u, j, n, k))
            clause.append(_var_index(v, j, n, k))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

