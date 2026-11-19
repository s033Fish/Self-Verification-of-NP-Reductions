"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instances are dictionaries with keys:

    n   – number of vertices (vertices are 0..n-1)
    edges – list of undirected edges, each edge is a two‑element list
    k   – size bound for the dominating set (we ask for a set of size ≤ k)

The target problem (Sat) expects instances of the form:

    {"num_vars": m, "clauses": [[lit, ...], ...]}

Variables are numbered from 1 to m.  A literal is a positive integer for a
positive occurrence and a negative integer for a negated occurrence.

The reduction creates a SAT formula that is satisfiable iff the given graph
has a dominating set of size at most ``k``.

Encoding strategy
------------------
* For each vertex ``v`` we introduce a Boolean variable ``x_v`` that is true
  exactly when ``v`` is chosen into the dominating set.
* For each vertex ``v`` and each *slot* ``s`` (``1 ≤ s ≤ k``) we introduce an
  auxiliary variable ``a_{v,s}``.  Intuitively ``a_{v,s}`` means “vertex ``v``
  occupies slot ``s``”.  The slots guarantee the cardinality constraint
  ``∑ x_v ≤ k`` while keeping the encoding polynomial:
    - If ``x_v`` is true, it must occupy at least one slot:
          (¬x_v ∨ a_{v,1} ∨ … ∨ a_{v,k})
    - If a vertex occupies a slot, it must be selected:
          (¬a_{v,s} ∨ x_v)
    - No slot can be occupied by two different vertices:
          (¬a_{v,s} ∨ ¬a_{w,s})   for all v < w.
* Domination constraints: for every vertex ``v`` we add a clause that at
  least one of ``v`` itself or one of its neighbours is selected:
        (x_v ∨ x_{u1} ∨ x_{u2} ∨ …)
  If ``v`` is isolated the clause reduces to ``(x_v)`` which forces the
  isolated vertex to be in the dominating set – matching the problem
  definition.

Edge‑case handling
-------------------
* ``k < 0`` – impossible, we output an unsatisfiable formula (a single empty
  clause).
* ``n == 0`` – the empty graph is always dominated; we output a trivially
  satisfiable formula (no clauses).
* ``k >= n`` – any set of at most ``k`` vertices works, so we again output a
  trivially satisfiable formula.
* ``k == 0`` – the only possible dominating set is the empty set, which can
  dominate only an empty graph.  For non‑empty graphs we force every ``x_v``
  to be false, making the formula unsatisfiable unless ``n == 0`` (already
  handled).

The function runs in polynomial time with respect to the size of the input
graph and ``k``.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating Set instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``n``, ``edges`` and ``k`` as described above.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # ---------------------------------------------------------------------
    # Edge‑case handling (mirroring the source problem's definition).
    # ---------------------------------------------------------------------
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    if n == 0:
        # Empty graph is always dominated; return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    if k >= n:
        # Any set works – return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    # ---------------------------------------------------------------------
    # Build adjacency list for domination constraints.
    # ---------------------------------------------------------------------
    adj: List[set] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # ---------------------------------------------------------------------
    # Variable numbering.
    #   1 .. n                -> x_v (vertex selected)
    #   n+1 .. n + n*k        -> a_{v,s} (slot assignment)
    # ---------------------------------------------------------------------
    cur = 1
    x_vars = []  # index -> SAT variable number for x_v
    for _ in range(n):
        x_vars.append(cur)
        cur += 1

    a_vars = {}  # (v, s) -> variable number
    if k > 0:
        for v in range(n):
            for s in range(1, k + 1):
                a_vars[(v, s)] = cur
                cur += 1

    num_vars = cur - 1
    clauses: List[List[int]] = []

    # ---------------------------------------------------------------------
    # Domination clauses: each vertex is either in D or adjacent to a vertex in D.
    # ---------------------------------------------------------------------
    for v in range(n):
        lits = [x_vars[v]]  # the vertex itself
        for u in adj[v]:
            lits.append(x_vars[u])
        clauses.append(lits)

    # ---------------------------------------------------------------------
    # Cardinality constraint (|D| ≤ k) using slot variables.
    # ---------------------------------------------------------------------
    if k == 0:
        # No vertex may be selected.
        for v in range(n):
            clauses.append([-x_vars[v]])
    else:
        # (1) If x_v is true, it must occupy at least one slot.
        for v in range(n):
            clause = [-x_vars[v]] + [a_vars[(v, s)] for s in range(1, k + 1)]
            clauses.append(clause)

        # (2) If a_{v,s} is true, then x_v is true.
        for v in range(n):
            for s in range(1, k + 1):
                clauses.append([-a_vars[(v, s)], x_vars[v]])

        # (3) No slot is used by two different vertices.
        for s in range(1, k + 1):
            for i in range(n):
                for j in range(i + 1, n):
                    clauses.append([-a_vars[(i, s)], -a_vars[(j, s)]])

    return {"num_vars": num_vars, "clauses": clauses}

