"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined by the ``Sat`` class in ``problems.py``.  An
instance is a dict ``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where
each literal is an integer ``+v`` (variable *v* true) or ``-v`` (variable *v*
false).  The target problem is the ``Clique`` class – a graph with vertices
``0..n-1`` and an integer ``k``; the answer is *yes* iff the graph contains a
clique of size at least ``k``.

We implement the classic polynomial‑time reduction:

* For each clause ``C_i`` and each literal ``ℓ`` in that clause we create a
  vertex.
* Two vertices from *different* clauses are connected by an edge unless the
  corresponding literals are contradictory – i.e. they refer to the same
  variable with opposite signs.
* The parameter ``k`` is set to the number of clauses.

Correctness sketch:
    *If the formula is satisfiable*, pick a true literal from each clause.
    The chosen vertices are pairwise non‑contradictory, hence they form a
    ``k``‑clique.
    *Conversely*, any ``k``‑clique selects exactly one vertex from each clause
    (otherwise two vertices would share a clause and would not be adjacent).
    The literals of the selected vertices are mutually non‑contradictory, so
    they define a consistent assignment satisfying every clause.

Edge‑case handling matches the specifications of both problems:
    * An empty list of clauses is trivially satisfiable.  We output a graph with
      ``k = 0`` (the Clique problem answers *yes* for any ``k <= 0``).
    * If any clause is empty, the formula is unsatisfiable.  We output a graph
      with ``n = 0`` and ``k = number_of_clauses``; because ``k > n`` the Clique
      instance is a guaranteed *no*.

The implementation runs in time linear in the total number of literals and
quadratic in the number of clauses – polynomial in the input size.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import Sat, Clique


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary following the ``Sat`` specification.

    Returns
    -------
    dict
        A dictionary following the ``Clique`` specification such that the
        answer to the Clique instance is *yes* exactly when the SAT instance
        is satisfiable.
    """
    # Validate the source instance (will raise if malformed).
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case 1: no clauses → trivially satisfiable.
    if num_clauses == 0:
        # Any graph works; we choose the empty graph with k = 0.
        return {"n": 0, "edges": [], "k": 0}

    # Edge case 2: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        # Return a graph where k > n, guaranteeing a NO answer.
        return {"n": 0, "edges": [], "k": num_clauses}

    # Normal case: build vertices for each literal occurrence.
    # Assign a unique integer id to each (clause_index, literal) pair.
    vertex_ids: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_ids.append((ci, lit))

    n = len(vertex_ids)
    # Build adjacency list of edges.
    edges: List[List[int]] = []
    # Helper to test contradiction: same variable, opposite sign.
    def contradictory(l1: int, l2: int) -> bool:
        return abs(l1) == abs(l2) and l1 != l2

    # For each unordered pair of vertices, add edge if they are from different
    # clauses and not contradictory.
    for i in range(n):
        ci, li = vertex_ids[i]
        for j in range(i + 1, n):
            cj, lj = vertex_ids[j]
            if ci == cj:
                continue  # same clause – no edge
            if contradictory(li, lj):
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": num_clauses}

