"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where the vertices are ``0..n-1`` and ``k`` is the size bound for a
 dominating set.  The target problem (Sat) expects a CNF instance::

    {"num_vars": m, "clauses": [[lit, ...], ...]}

A literal is an integer ``+v`` (meaning variable ``v`` is true) or ``-v``
meaning variable ``v`` is false.  Variables are numbered from ``1`` to
 ``m``.

The reduction creates a set of Boolean variables ``y_{i,t}`` where ``i``
 ranges over vertices (``0..n-1``) and ``t`` ranges over the positions
 ``1..k``.  Intuitively, ``y_{i,t}`` is true iff vertex ``i`` occupies the
 ``t``‑th slot of the dominating set.  Because there are only ``k`` slots,
 the construction guarantees that at most ``k`` vertices are selected.

Constraints encoded as clauses:

1. **At most one vertex per position** – for each position ``t`` and any
   two distinct vertices ``i`` and ``j`` we add ``(-y_{i,t} ∨ -y_{j,t})``.
2. **A vertex occupies at most one position** – for each vertex ``i`` and
   any two distinct positions ``t`` and ``t'`` we add ``(-y_{i,t} ∨ -y_{i,t'})``.
3. **Domination** – for every vertex ``v`` we add a clause that requires
   it to be dominated: the clause is the disjunction of all variables
   ``y_{u,t}`` where ``u`` is either ``v`` itself or a neighbor of ``v``
   and ``t`` ranges over ``1..k``.

The construction is polynomial in ``n`` and ``k`` (the number of
variables is ``n·k`` and the number of clauses is ``O(k·n^2)``).

Edge‑case handling mirrors the definition of Dominating Set:

* ``k < 0`` – always unsatisfiable; we return a formula containing an
  empty clause.
* ``k == 0`` – satisfiable only when ``n == 0``; otherwise we also return
  an unsatisfiable formula.
* ``n == 0`` – trivially satisfiable (empty formula).
* ``k >= n`` – trivially satisfiable (any set of all vertices works),
  again we return an empty formula.

The function ``reduce`` implements the above logic and returns a valid
SAT instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating Set instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[List[int]], "k": int}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}``
    """

    n = instance.get("n", 0)
    edges = instance.get("edges", [])
    k = instance.get("k", 0)

    # ------------------------------------------------------------------
    # Simple edge‑case handling (mirrors DominatingSet.is_yes semantics).
    # ------------------------------------------------------------------
    # Unsatisfiable cases: k < 0, or k == 0 with a non‑empty graph.
    if k < 0 or (k == 0 and n > 0):
        # A single empty clause makes the formula unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # Trivially satisfiable cases: empty graph, or k >= n.
    if n == 0 or k >= n:
        # An empty formula (no clauses) is always satisfiable.
        return {"num_vars": 0, "clauses": []}

    # ------------------------------------------------------------------
    # Build adjacency list for quick neighbor lookup.
    # ------------------------------------------------------------------
    adj: List[set] = [set() for _ in range(n)]
    for u, v in edges:
        # The problem statement guarantees 0 <= u, v < n and u != v.
        adj[u].add(v)
        adj[v].add(u)

    # Helper to map (vertex i, position t) to a SAT variable index.
    # Variables are numbered from 1 to n*k inclusive.
    def var(i: int, t: int) -> int:
        return i * k + t  # i in [0, n-1], t in [1, k]

    num_vars = n * k
    clauses: List[List[int]] = []

    # ---------------------------------------------------------------
    # 1. At most one vertex per position t.
    # ---------------------------------------------------------------
    for t in range(1, k + 1):
        for i in range(n):
            vi = var(i, t)
            for j in range(i + 1, n):
                vj = var(j, t)
                clauses.append([-vi, -vj])

    # ---------------------------------------------------------------
    # 2. A vertex occupies at most one position.
    # ---------------------------------------------------------------
    for i in range(n):
        for t in range(1, k + 1):
            vt = var(i, t)
            for tp in range(t + 1, k + 1):
                vtp = var(i, tp)
                clauses.append([-vt, -vtp])

    # ---------------------------------------------------------------
    # 3. Domination constraints.
    #    For each vertex v, the clause is the disjunction of all
    #    variables representing v or any neighbor of v in any position.
    # ---------------------------------------------------------------
    for v in range(n):
        clause: List[int] = []
        # Include v itself and all its neighbors.
        candidates = [v] + list(adj[v])
        for u in candidates:
            for t in range(1, k + 1):
                clause.append(var(u, t))
        # The clause is guaranteed to be non‑empty because at least v
        # appears.
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

