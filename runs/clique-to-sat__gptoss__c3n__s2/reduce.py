"""Reduction from Clique to SAT.

The source problem is :class:`Clique` defined in ``problems.py``.  An
instance is a dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The target problem is :class:`Sat`.  An instance is a dictionary
``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where literals are
signed integers as described in the problem statement.

The reduction works as follows (standard textbook reduction):

* If ``k <= 0`` the answer is always *yes*.  We return a trivially
  satisfiable formula – a CNF with zero variables and zero clauses.
* If ``k > n`` the answer is always *no*.  We return an unsatisfiable
  formula – a CNF containing a single empty clause.
* Otherwise we encode the existence of a *clique of size exactly k*.
  (If a larger clique exists we can simply choose any k of its vertices.)

Encoding details
-----------------
We introduce a Boolean variable ``x_{i,p}`` meaning *vertex i occupies
position p* in the ordered selection of k vertices.  Positions are numbered
``0 .. k-1``.  The total number of variables is ``n * k``; variable IDs are
assigned in the natural order ``id = i * k + p + 1`` (SAT variables are 1‑based).

Constraints (each becomes one or more CNF clauses):

1. **Every position is occupied** – for each position ``p`` we add a clause
   ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p})``.
2. **At most one vertex per position** – for each position ``p`` and each
   distinct pair of vertices ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.
3. **A vertex occupies at most one position** – for each vertex ``i`` and
   each distinct pair of positions ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.
4. **Selected vertices must be pairwise adjacent** – for every *non‑edge*
   ``(i, j)`` (i.e., ``i != j`` and ``{i, j}`` not in the edge set) and for
   every pair of distinct positions ``p != q`` we add the clause
   ``(¬x_{i,p} ∨ ¬x_{j,q})``.  This forbids placing non‑adjacent vertices in
   the selection.

All these clauses are added to the output CNF.  The construction is
polynomial in ``n`` and ``k`` (the number of clauses is O(n²k + nk²)).

The function validates the input using ``Clique.validate`` and returns a
dictionary suitable for ``Sat.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, Sat


def _var_id(i: int, p: int, k: int) -> int:
    """Map vertex ``i`` and position ``p`` to a SAT variable id (1‑based)."""
    return i * k + p + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned instance satisfies ``Sat.validate`` and is satisfiable
    exactly when the input graph contains a clique of size at least ``k``.
    """
    # Validate the source instance first – this will raise InvalidInstance on error.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling according to the problem statement.
    if k <= 0:
        # Always yes – empty CNF (no clauses) is trivially satisfiable.
        return {"num_vars": 0, "clauses": []}
    if n == 0:
        # No vertices; k>0 implies answer is no.
        return {"num_vars": 0, "clauses": [[]]}
    if k == 1:
        # Any single vertex forms a clique of size 1 when n>=1.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Impossible – return an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    clauses: List[List[int]] = []

    # 1. Every position must be occupied by at least one vertex.
    for p in range(k):
        clause = [_var_id(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, p, k), -_var_id(j, p, k)])

    # 3. A vertex appears in at most one position.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_id(i, p, k), -_var_id(i, q, k)])

    # 4. Non‑edges cannot both be selected.
    # Compute all unordered non‑edge pairs (i, j) with i < j.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                for p in range(k):
                    for q in range(k):
                        if p == q:
                            continue  # already prevented by (2)
                        clauses.append([-_var_id(i, p, k), -_var_id(j, q, k)])

    num_vars = n * k
    return {"num_vars": num_vars, "clauses": clauses}

