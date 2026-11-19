"""Reduction from Vertex Cover to SAT.

The source problem (VertexCover) instance format is a dictionary:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1, edges are undirected, and ``k`` may be any
integer.

The target problem (Sat) instance format is a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: a positive integer ``v`` denotes
the variable ``v`` being true, and a negative integer ``-v`` denotes the
variable ``v`` being false.  An empty list of clauses is trivially satisfiable;
the presence of an empty clause (``[]``) makes the formula unsatisfiable.

We implement a classic polynomial‑time many‑one reduction.  For each vertex
``i`` (0 ≤ i < n) and each position ``j`` in a potential cover (0 ≤ j < k) we
introduce a Boolean variable ``x_{j,i}`` that is true exactly when the vertex
``i`` occupies position ``j`` in the chosen cover of size at most ``k``.

The CNF encodes three groups of constraints:

1. **Each position selects at least one vertex** – a clause containing all
   variables of that position.
2. **Each position selects at most one vertex** – for every pair of distinct
   vertices ``i`` and ``i'`` in the same position we add the clause
   ``(-x_{j,i} ∨ -x_{j,i'})``.
   (Allowing the same vertex to appear in multiple positions does not hurt
   correctness because it still yields a cover of size ≤ k.)
3. **Every edge is incident to a selected vertex** – for each edge ``(u, v)``
   we add a clause that, for each position, includes the literals
   ``x_{j,u}`` and ``x_{j,v}``.  The clause is satisfied iff at least one of the
   k positions chooses ``u`` or ``v``.

Edge cases are handled explicitly to keep the reduction simple and to avoid
creating a large formula when it is unnecessary:

* ``k < 0`` – the vertex‑cover instance is always a NO instance.  We output a
  SAT instance containing a single empty clause, which is unsatisfiable.
* ``k == 0`` – the answer is YES iff the graph has no edges.  We return an
  empty‑clause list for the YES case and an unsatisfiable instance otherwise.
* ``k >= n`` – any set of at most ``k`` vertices can cover the graph, so we
  return an empty formula (always satisfiable).
* The graph has no edges – also always YES, handled by returning an empty
  formula.

The reduction runs in time polynomial in ``n``, ``|E|`` and ``k`` and produces
``m = n * k`` variables and a number of clauses that is O(k·n² + k·|E|), which is
polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        above.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Helper to produce an unsatisfiable SAT instance.
    def unsat_instance() -> Dict[str, Any]:
        # One variable is enough; the empty clause makes the formula unsat.
        return {"num_vars": 1, "clauses": [[]]}

    # Helper to produce a trivially satisfiable SAT instance.
    def sat_instance() -> Dict[str, Any]:
        return {"num_vars": 1, "clauses": []}

    # Edge cases -----------------------------------------------------------
    if k < 0:
        return unsat_instance()

    if not edges:  # No edges – always yes for any k >= 0.
        return sat_instance()

    if k == 0:
        # No edges case already handled; with k==0 and at least one edge the
        # answer is NO.
        return unsat_instance()

    if k >= n:
        # We can always pick all vertices (or fewer) to cover the graph.
        return sat_instance()

    # General case --------------------------------------------------------
    # Number of variables: one for each (position, vertex) pair.
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Each position must select at least one vertex.
    for j in range(k):
        clause = []
        base = j * n
        for i in range(n):
            clause.append(base + i + 1)  # positive literal
        clauses.append(clause)

    # 2. Each position selects at most one vertex (pairwise mutual exclusion).
    for j in range(k):
        base = j * n
        for i in range(n):
            for i2 in range(i + 1, n):
                clauses.append([-(base + i + 1), -(base + i2 + 1)])

    # 3. Edge coverage: for each edge, at least one endpoint appears in some
    #    position.
    for u, v in edges:
        clause = []
        for j in range(k):
            base = j * n
            clause.append(base + u + 1)
            clause.append(base + v + 1)
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

