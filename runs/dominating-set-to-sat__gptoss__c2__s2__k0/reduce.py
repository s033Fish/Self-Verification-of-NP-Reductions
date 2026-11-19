"""Reduction from Dominating Set to SAT.

The source problem is DominatingSet with instances of the form::

    {"n": int, "edges": [[u, v], ...], "k": int}

The target problem is SAT with instances of the form::

    {"num_vars": int, "clauses": [[literal, ...], ...]}

The reduction creates a Boolean variable ``x_v`` for each vertex ``v``
indicating whether ``v`` is chosen in the dominating set.  For each
vertex we add a clause that guarantees it is either chosen itself or
has a neighbour that is chosen.  Finally we enforce the cardinality
constraint ``|D| <= k`` using the classic *sequential counter* encoding
by Sinz (2005).  This encoding introduces auxiliary variables ``s_{i,j}``
meaning “among the first *i* vertices at least *j* of the ``x`` variables
are true”.  The set of clauses added for the counter is polynomial in
``n`` and ``k`` (``O(n·k)``) and guarantees that at most ``k`` vertices
are selected.

Edge‑case handling:
* ``k < 0`` – the source instance is always a NO instance.  We return a
  SAT formula containing a single empty clause, which is unsatisfiable.
* ``n == 0`` – the source instance is trivially YES for any ``k >= 0``.
  We return an empty SAT formula (no clauses), which is always
  satisfiable.
* ``k == 0`` – we simply force all ``x_v`` to be false with unit
  clauses.  The domination clauses will then make the formula unsat
  unless the graph is empty, matching the source semantics.

The function ``reduce`` performs the transformation and returns the
SAT instance as a Python dictionary matching the format described
above.
"""

from typing import List, Dict


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating Set instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``n``, ``edges`` and ``k`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 → always NO.
    if k < 0:
        # An empty clause [] makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Edge case: empty graph.
    if n == 0:
        # No variables and no clauses – always satisfiable.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list.
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    clauses: List[List[int]] = []
    next_var = 1

    # Primary variables x_v (1‑based IDs).
    x_vars: List[int] = []
    for _ in range(n):
        x_vars.append(next_var)
        next_var += 1

    # Domination clauses: each vertex is dominated by itself or a neighbour.
    for v in range(n):
        clause = [x_vars[v]] + [x_vars[u] for u in adj[v]]
        # Remove duplicates just in case (not strictly necessary).
        clause = list(dict.fromkeys(clause))
        clauses.append(clause)

    # Cardinality constraint |D| <= k.
    if k == 0:
        # Force all x_vars to be false.
        for xv in x_vars:
            clauses.append([-xv])
        return {"num_vars": next_var - 1, "clauses": clauses}

    # If k >= n the cardinality constraint is automatically satisfied;
    # we can safely omit the counter.
    if k >= n:
        return {"num_vars": next_var - 1, "clauses": clauses}

    # Sequential counter variables s_{i,j} for i=1..n, j=1..k.
    s_vars: List[List[int]] = [[0] * (k + 1) for _ in range(n + 1)]  # 1‑based indexing
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            s_vars[i][j] = next_var
            next_var += 1

    # Helper to add a clause.
    def add_clause(lits: List[int]):
        clauses.append(lits)

    # 1) First vertex constraints.
    # (¬x_1 ∨ s_{1,1})
    add_clause([-x_vars[0], s_vars[1][1]])
    # (¬s_{1,1} ∨ x_1) is not required for the at‑most‑k encoding.

    # 2) Remaining vertices.
    for i in range(2, n + 1):
        xi = x_vars[i - 1]
        # (¬x_i ∨ s_{i,1})
        add_clause([-xi, s_vars[i][1]])
        for j in range(1, k + 1):
            # (¬s_{i-1,j} ∨ s_{i,j})
            add_clause([-s_vars[i - 1][j], s_vars[i][j]])
        for j in range(2, k + 1):
            # (¬x_i ∨ ¬s_{i-1,j-1} ∨ s_{i,j})
            add_clause([-xi, -s_vars[i - 1][j - 1], s_vars[i][j]])
        # (¬s_{i-1,k} ∨ ¬x_i) – prevents exceeding k.
        add_clause([-s_vars[i - 1][k], -xi])

    # The counter guarantees that at most k of the x‑variables are true.
    return {"num_vars": next_var - 1, "clauses": clauses}

