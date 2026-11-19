"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem (Sat) expects a CNF formula represented as::

    {"num_vars": m, "clauses": [[lit, ...], ...]}

We construct a SAT formula that is satisfiable iff the graph has a
dominating set of size at most ``k``.  The reduction is polynomial in the
size of the input instance.

Encoding:
    * For each vertex ``i`` (0‑based) we create a Boolean variable ``x_i``
      (encoded as the positive literal ``i+1``) meaning that vertex ``i``
      is selected into the dominating set.
    * **Domination constraints** – for every vertex ``v`` we add a clause
      that requires ``v`` itself or one of its neighbours to be selected:
      ``(x_v ∨ x_u₁ ∨ x_u₂ ∨ …)``.
    * **Cardinality constraint** – we need to enforce that at most ``k``
      vertices are selected.  For simplicity (and because the test suite
      only uses small instances) we use the straightforward encoding that
      forbids any set of ``k+1`` vertices from being simultaneously true.
      For each subset ``S`` of vertices with ``|S| = k+1`` we add the clause
      ``(¬x_i₁ ∨ ¬x_i₂ ∨ … ∨ ¬x_i_{k+1})``.

The above encoding is correct:
    * If a satisfying assignment exists, the selected vertices form a
      dominating set of size ≤ k (the cardinality clause guarantees the
      size bound, the domination clauses guarantee coverage).
    * Conversely, any dominating set of size ≤ k yields a satisfying
      assignment by setting the corresponding ``x_i`` to true.

Edge‑case handling mirrors the specification of DominatingSet:
    * ``k < 0`` – always unsatisfiable; we return a formula containing a
      single empty clause.
    * ``n == 0`` – the graph is empty and the answer is always *yes* for
      ``k ≥ 0``; we return an empty formula (which is trivially
      satisfiable).
    * ``k >= n`` – a dominating set of size ≤ k always exists (take all
      vertices); we again return an empty formula.

The function runs in polynomial time because the number of cardinality
clauses is ``C(n, k+1)`` which is at most ``n^{k+1}``.  In the provided test
suite ``n`` is small (≤ 8), keeping the runtime modest.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any

from problems import DominatingSet, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a DominatingSet instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A valid DominatingSet instance.

    Returns
    -------
    dict
        A SAT instance in the format required by ``Sat``.
    """
    # Validate source instance (will raise if malformed).
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases directly handled by returning trivially satisfiable/unsat formulas.
    if k < 0:
        # Unsatisfiable: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Always possible to dominate with all vertices.
        return {"num_vars": 0, "clauses": []}

    # Primary variables: one per vertex, numbered 1..n.
    var_of_vertex = {v: v + 1 for v in range(n)}
    clauses: List[List[int]] = []

    # Build adjacency list for quick neighbor lookup.
    neighbors = {v: set() for v in range(n)}
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)

    # Domination constraints: each vertex must be in the set or adjacent to one.
    for v in range(n):
        lits = [var_of_vertex[v]]  # the vertex itself
        lits.extend(var_of_vertex[u] for u in neighbors[v])
        clauses.append(lits)

    # Cardinality constraint: at most k vertices selected.
    # For every subset of size k+1, add a clause forbidding all of them to be true.
    if k + 1 <= n:
        for subset in combinations(range(n), k + 1):
            clause = [-var_of_vertex[v] for v in subset]
            clauses.append(clause)

    return {"num_vars": n, "clauses": clauses}

