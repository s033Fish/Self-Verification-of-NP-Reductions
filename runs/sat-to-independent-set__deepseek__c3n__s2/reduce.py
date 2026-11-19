"""Polynomial-time reduction from SAT (CNF) to Independent Set.

Construction
------------
Given a CNF instance ``{"num_vars": m, "clauses": [...]}``:

* For every *literal occurrence* in every clause create one vertex.  (A
  clause with repeated literals therefore contributes several vertices; an
  empty clause contributes none.)
* Add an edge between every pair of vertices that come from the *same*
  clause.  This makes each clause a clique, so an independent set can pick
  at most one literal occurrence per clause.
* Add an edge between every pair of vertices whose literals are
  *complementary* (``v`` and ``-v``).  This forbids choosing both a literal
  and its negation.
* Set ``k`` to the number of clauses.

Correctness
-----------
Let ``c`` be the number of clauses and ``V`` the number of vertices.

* If the formula is satisfiable, pick for each clause one true literal
  occurrence.  These ``c`` vertices are pairwise non-adjacent: at most one
  per clause, and no two are complementary because all are true.  Hence
  there is an independent set of size ``c = k``.
* Conversely, any independent set has at most one vertex per clause, hence
  size at most ``c = k``.  An independent set of size ``>= k`` therefore has
  exactly one vertex per clause and contains no complementary pair, so the
  literals it selects are consistent and each clause has a true literal;
  the induced assignment satisfies the formula.

Edge cases fall out directly: no clauses gives ``k = 0`` (always yes); an
empty clause gives fewer than ``k`` vertices (``k > n``, always no).

The construction uses O(V^2) edges and runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # vertices[i] is the literal occurrence represented by vertex i.
    vertices: list[int] = []

    clause_vertices: list[list[int]] = []
    for clause in clauses:
        group: list[int] = []
        for literal in clause:
            group.append(len(vertices))
            vertices.append(literal)
        clause_vertices.append(group)

    # Collect edges in a set so that a pair arising both as a within-clause
    # edge and as a complementary-literal edge is only emitted once.
    edge_set: set[frozenset[int]] = set()

    # Clique edges inside each clause.
    for group in clause_vertices:
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                edge_set.add(frozenset((group[i], group[j])))

    # Complementary-literal edges.
    # Group vertices by literal value, then pair each literal with its negation.
    by_literal: dict[int, list[int]] = {}
    for vertex, literal in enumerate(vertices):
        by_literal.setdefault(literal, []).append(vertex)

    for literal, group in by_literal.items():
        if literal < 0:
            continue  # handle each complementary pair once via the positive literal
        for other in by_literal.get(-literal, []):
            for vertex in group:
                edge_set.add(frozenset((vertex, other)))

    edges = [sorted(edge) for edge in edge_set]
    return {"n": len(vertices), "edges": edges, "k": len(clauses)}
