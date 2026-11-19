"""Reduction from Clique to SAT.

The source problem is :class:`Clique` defined in ``problems.py``.  An instance
is a dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}`` where the graph
has vertices ``0..n-1`` and ``edges`` is a list of undirected edges.

The target problem is :class:`Sat`.  An instance is a dictionary
``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where literals are
signed integers ``+v`` (variable *v* true) or ``-v`` (variable *v* false).

The reduction creates a CNF formula that is satisfiable iff the input graph
contains a clique of size at least ``k``.

Standard textbook reduction:

* Introduce a Boolean variable ``x_{i, v}`` for each position ``i`` in the
  potential clique (``0 <= i < k``) and each vertex ``v`` (``0 <= v < n``).
  Variable IDs are numbered from ``1`` to ``k * n`` using the mapping
  ``id = i * n + v + 1``.

* **At least one vertex per position** – for each ``i`` add the clause
  ``(x_{i,0} ∨ x_{i,1} ∨ … ∨ x_{i,n-1})``.

* **At most one vertex per position** – for each ``i`` and each pair
  ``v != w`` add ``(¬x_{i,v} ∨ ¬x_{i,w})``.

* **A vertex is used at most once** – for each vertex ``v`` and each pair of
  positions ``i < j`` add ``(¬x_{i,v} ∨ ¬x_{j,v})``.

* **Non‑edges are forbidden** – for each pair of positions ``i < j`` and each
  unordered pair of vertices ``{u, v}`` that is **not** an edge, add the clause
  ``(¬x_{i,u} ∨ ¬x_{j,v})``.  This guarantees that any two selected vertices
  are adjacent.

Edge cases are handled explicitly to keep the output small and to avoid
creating unnecessary variables:

* ``k <= 0`` – the answer is always *yes*.  We return a trivially satisfiable
  SAT instance with ``num_vars = 0`` and no clauses.
* ``k > n`` – the answer is always *no*.  We return an unsatisfiable instance
  containing a single empty clause ``[]``.

The function runs in time polynomial in ``n`` and ``k`` (``O(k^2 * n^2)``
clauses in the worst case) which satisfies the requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, Sat


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Convert list of edges to a set of unordered vertex pairs.

    The input follows the format of ``Clique`` where each edge appears only
    once and ``[u, v]`` and ``[v, u]`` are considered identical.
    """

    return {frozenset((u, v)) for u, v in edges}


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance.  It is assumed to be
        validated by ``Clique.validate`` (the caller may invoke it before
        calling ``reduce``).

    Returns
    -------
    dict
        A SAT instance dictionary compatible with ``Sat.validate``.
    """

    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed, mirroring the behaviour expected by the benchmark.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases ------------------------------------------------------------
    if k <= 0:
        # Always yes – empty formula (no clauses) is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no – a single empty clause makes the formula unsatisfiable.
        return {"num_vars": max(0, k * n), "clauses": [[]]}

    # General case ----------------------------------------------------------
    # Variable mapping: (i, v) -> id in 1..k*n
    def var_id(i: int, v: int) -> int:
        return i * n + v + 1

    clauses: List[List[int]] = []

    # 1. At least one vertex for each position i
    for i in range(k):
        clause = [var_id(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position i (pairwise mutual exclusion)
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var_id(i, v), -var_id(i, w)])

    # 3. A vertex cannot appear in two different positions
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var_id(i, v), -var_id(j, v)])

    # 4. Non‑edge constraints
    edge_set = _edge_set(edges)
    # For each unordered pair of distinct vertices that is NOT an edge, add
    # constraints for every ordered pair of positions i < j.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v:
                        continue
                    if frozenset((u, v)) not in edge_set:
                        clauses.append([-var_id(i, u), -var_id(j, v)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

