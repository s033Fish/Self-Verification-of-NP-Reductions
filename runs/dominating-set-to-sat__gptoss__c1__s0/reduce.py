"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format is::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 .. n-1``.  ``edges`` contains each undirected edge
once (order does not matter) and ``k`` may be any integer.

The target problem (Sat) instance format is::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1 .. m``.  A literal is a signed integer – ``+v``
means variable ``v`` is true, ``-v`` means it is false.  An empty clause is
unsatisfiable, a formula with no clauses is always satisfiable.

We construct a CNF formula that is satisfiable iff the input graph has a
dominating set of size *at most* ``k``.  The construction uses a standard
sequential‑counter encoding (Sinz, 2005) to enforce the cardinality bound
polynomially.

Variables:
    * For each vertex ``i`` (0‑based) we introduce a Boolean variable ``d_i``
      (encoded as SAT variable ``i+1``) that is true exactly when vertex ``i``
      belongs to the dominating set.
    * For the at‑most‑``k`` constraint we introduce auxiliary variables
      ``s_{i,j}`` for ``i = 1..n`` and ``j = 1..k``.  ``s_{i,j}`` is true iff
      among the first ``i`` vertices at least ``j`` of them are selected.
      These are encoded after the ``d_i`` variables.

Clauses:
    1. **Domination** – for each vertex ``v`` we add a clause requiring that
       ``v`` itself or one of its neighbours is selected:
          (d_v ∨ d_u₁ ∨ d_u₂ ∨ … )
       If a vertex has no neighbours the clause reduces to a unit clause
       ``[d_v]``, forcing it into the set (which matches the problem statement).

    2. **Sequential counter** – the following clauses encode the condition
       that at most ``k`` of the ``d_i`` variables are true (Sinz, 2005):

       a) (¬d_i ∨ s_{i,1})                         for i = 1..n
       b) (¬s_{i‑1,j} ∨ s_{i,j})                    for i = 2..n, j = 1..k
       c) (¬d_i ∨ ¬s_{i‑1,j‑1} ∨ s_{i,j})           for i = 2..n, j = 2..k
       d) (¬s_{i‑1,k} ∨ ¬d_i)                       for i = 2..n

    The auxiliary variables are numbered as ``aux(i, j) = n + (i‑1)*k + j``.

Edge cases are handled explicitly to keep the reduction simple and to avoid
creating unnecessary variables:

* ``k < 0`` – the answer is always *no*.  We return an unsatisfiable formula
  consisting of a single empty clause.
* ``n == 0`` – the graph is empty.  The answer is *yes* for any ``k >= 0``;
  we return a trivially satisfiable formula (zero clauses, zero variables).
* ``k >= n`` – any set of vertices dominates the graph, so the answer is *yes*;
  we again return a trivially satisfiable formula.
* ``k == 0`` (and ``n > 0``) – a dominating set of size 0 cannot exist, so we
  return an unsatisfiable formula.

The function runs in time polynomial in ``n + |E| + k`` and uses at most
``n + n*k`` variables, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _aux_var(n: int, k: int, i: int, j: int) -> int:
    """Return the SAT variable index for auxiliary s_{i,j}.

    ``i`` is 1‑based (1..n) and ``j`` is 1‑based (1..k).  The first ``n``
    variables are the vertex selection variables ``d_0 .. d_{n-1}``.
    """
    return n + (i - 1) * k + j


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the expected format.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])
    k: int = instance.get("k", 0)

    # Edge‑case handling ---------------------------------------------------
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Trivially satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # Non‑empty graph cannot have a dominating set of size 0.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency list for domination clauses.
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        if 0 <= u < n and 0 <= v < n and u != v:
            adj[u].append(v)
            adj[v].append(u)

    clauses: List[List[int]] = []

    # 1. Domination clauses.
    for v in range(n):
        clause = [v + 1]  # d_v variable (positive literal)
        for nb in adj[v]:
            clause.append(nb + 1)
        clauses.append(clause)

    # 2. Sequential counter clauses (only if k > 0).
    if k > 0:
        # a) (¬d_i ∨ s_{i,1}) for i = 1..n
        for i in range(1, n + 1):
            clauses.append([-i, _aux_var(n, k, i, 1)])

        # b) (¬s_{i-1,j} ∨ s_{i,j}) for i = 2..n, j = 1..k
        for i in range(2, n + 1):
            for j in range(1, k + 1):
                clauses.append([-_aux_var(n, k, i - 1, j), _aux_var(n, k, i, j)])

        # c) (¬d_i ∨ ¬s_{i-1,j-1} ∨ s_{i,j}) for i = 2..n, j = 2..k
        for i in range(2, n + 1):
            for j in range(2, k + 1):
                clauses.append([-i, -_aux_var(n, k, i - 1, j - 1), _aux_var(n, k, i, j)])

        # d) (¬s_{i-1,k} ∨ ¬d_i) for i = 2..n
        for i in range(2, n + 1):
            clauses.append([-_aux_var(n, k, i - 1, k), -i])

    # Total number of variables = n (d_i) + n*k (auxiliary)
    num_vars = n + n * k if k > 0 else n

    return {"num_vars": num_vars, "clauses": clauses}

