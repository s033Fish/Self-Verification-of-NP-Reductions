"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format is a dictionary:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1, edges are undirected, and we ask whether the
graph has a dominating set of size at most *k*.

The target problem (Sat) instance format is a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where literals are integers +v (variable v true) or -v (variable v false).

We construct a polynomial‑size CNF formula that is satisfiable iff the
given graph has a dominating set of size ≤ k.  The construction follows a
standard encoding using *k* “position” variables.  For each position p
∈ {0,…,k‑1} and each vertex v we create a Boolean variable x_{p,v} that is
true exactly when vertex *v* occupies position *p* in the dominating set.

Constraints encoded:
  1. **Each position chooses at least one vertex** – a clause containing
     all x_{p,v} for a fixed p.
  2. **No vertex appears in two different positions** – for every vertex
     v and every pair of distinct positions p<q we add the clause
     (¬x_{p,v} ∨ ¬x_{q,v}).
  3. **Domination** – for every vertex v we require that some selected
     vertex (either v itself or one of its neighbours) appears in *some*
     position.  This yields a clause that is the disjunction of all
     x_{p,u} where u is v or a neighbour of v, for all positions p.

The construction is polynomial in n, |E| and k (O(k·n + k·|E|) variables
and clauses).  Edge cases are handled explicitly to match the semantics of
Dominating Set:
    * k < 0 → always unsatisfiable.
    * n = 0 → trivially satisfiable (empty formula).
    * k ≥ n → trivially satisfiable (any set of ≤ n vertices works).
    * k = 0 and n > 0 → unsatisfiable (the domination clause becomes an
      empty clause).

The function ``reduce`` implements this mapping.
"""

from __future__ import annotations
from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # ------------------------------------------------------------------
    # Edge‑case handling – these must match the source problem's answer.
    # ------------------------------------------------------------------
    if k < 0:
        # Unsatisfiable: introduce a single variable with an empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    if n == 0:
        # Empty graph is always dominated, regardless of k (k ≥ 0 here).
        return {"num_vars": 0, "clauses": []}

    if k >= n:
        # A dominating set of size ≤ n always exists (the whole vertex set).
        return {"num_vars": 0, "clauses": []}

    # ------------------------------------------------------------------
    # Build adjacency list for quick neighbour lookup.
    # ------------------------------------------------------------------
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # ------------------------------------------------------------------
    # Create variables x_{p,v} where p ∈ {0,…,k-1} and v ∈ {0,…,n-1}.
    # Variable indices start at 1 as required by the SAT format.
    # ------------------------------------------------------------------
    var_index: dict[tuple[int, int], int] = {}
    next_var = 1
    for p in range(k):
        for v in range(n):
            var_index[(p, v)] = next_var
            next_var += 1
    num_vars = next_var - 1

    clauses: List[List[int]] = []

    # 1) Each position must select at least one vertex.
    for p in range(k):
        clause = [var_index[(p, v)] for v in range(n)]
        clauses.append(clause)

    # 2) No vertex may appear in two different positions.
    for v in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-var_index[(p, v)], -var_index[(q, v)]])

    # 3) Domination constraints.
    #    For each vertex v, at least one of the selected vertices (itself
    #    or a neighbour) must appear in some position.
    for v in range(n):
        clause: List[int] = []
        # Variables corresponding to v itself.
        for p in range(k):
            clause.append(var_index[(p, v)])
        # Variables corresponding to neighbours of v.
        for u in adj[v]:
            for p in range(k):
                clause.append(var_index[(p, u)])
        # If the clause ends up empty (possible only when k == 0), the
        # SAT instance is unsatisfiable, which correctly mirrors the source
        # problem's answer for k == 0 and n > 0.
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

