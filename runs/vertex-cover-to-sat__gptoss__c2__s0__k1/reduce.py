"""Reduction from Vertex Cover to SAT.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled 0 … n‑1), ``edges`` is a list
of undirected edges and ``k`` is the size bound for the vertex cover.

The target problem (Sat) expects an instance of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered from ``1`` to ``m``.  A literal is a positive integer
``v`` (meaning *v* is true) or a negative integer ``-v`` (meaning *v* is false).

The reduction encodes the existence of a vertex cover of size **at most** ``k``
as a SAT formula.  For the non‑trivial case ``0 < k < n`` we introduce a set of
variables ``x_{i,v}`` where ``i`` (0‑based) denotes the *i*‑th slot of the cover
and ``v`` denotes a vertex.  Variable ``x_{i,v}`` is true iff vertex ``v`` is
chosen for slot ``i``.  The following constraints are added:

1. **Each slot chooses at least one vertex** – a clause containing all
   ``x_{i,v}`` for a fixed ``i``.
2. **A slot chooses at most one vertex** – for every pair ``v < w`` a clause
   ``(-x_{i,v} ∨ -x_{i,w})``.
3. **A vertex is used in at most one slot** – for every vertex ``v`` and every
   pair of slots ``i < j`` a clause ``(-x_{i,v} ∨ -x_{j,v})``.
4. **Every edge is covered** – for each edge ``(u, v)`` a clause that is the
   disjunction of all variables that select either endpoint in any slot:
   ``(x_{0,u} ∨ x_{0,v} ∨ … ∨ x_{k‑1,u} ∨ x_{k‑1,v})``.

These constraints guarantee that a satisfying assignment corresponds to a set
of exactly ``k`` distinct vertices covering all edges.  Because we enforce
*exactly* ``k`` vertices, the reduction is correct for the original “at most k”
question: if a cover of size ≤ k exists, we can extend it arbitrarily to size
exactly ``k`` by adding unused vertices (possible because ``k < n`` in this
branch).  Conversely, any satisfying assignment yields a cover of size ≤ k.

Edge‑case handling:

* ``k < 0`` – always a *no* instance.  We output an unsatisfiable formula (a
  single empty clause).
* ``k == 0`` – the answer is *yes* iff the graph has no edges.  We output a
  trivially satisfiable formula when there are no edges, otherwise an
  unsatisfiable one.
* ``k >= n`` – always a *yes* instance because all vertices can be taken.  We
  output a trivially satisfiable formula (no clauses).

The construction runs in polynomial time and produces a formula whose size
is ``O(k·n² + |E|·k)``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

def _var_id(i: int, v: int, n: int) -> int:
    """Map slot ``i`` and vertex ``v`` to a SAT variable number (1‑based).

    Variables are ordered first by slot, then by vertex:
    ``id = i * n + v + 1``.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a SAT instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        above.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Edge cases -----------------------------------------------------------
    # 1. k < 0 -> always NO
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}  # unsatisfiable (empty clause)

    # 2. k == 0 -> YES iff there are no edges
    if k == 0:
        if not edges:
            return {"num_vars": 0, "clauses": []}  # trivially satisfiable
        else:
            return {"num_vars": 1, "clauses": [[]]}

    # 3. k >= n -> always YES (take all vertices)
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # General case 0 < k < n --------------------------------------------
    num_vars = k * n
    clauses: List[List[int]] = []

    # (1) Each slot chooses at least one vertex
    for i in range(k):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # (2) Each slot chooses at most one vertex (pairwise)
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # (3) A vertex appears in at most one slot
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # (4) Edge coverage clauses
    for (u, v) in edges:
        clause = []
        for i in range(k):
            clause.append(_var_id(i, u, n))
            clause.append(_var_id(i, v, n))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

