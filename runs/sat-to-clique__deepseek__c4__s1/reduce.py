"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction:
  * One vertex per literal occurrence in each clause.
  * Join two vertices with an edge iff they come from different clauses and
    their literals are not complementary (i.e. not x and -x).
  * Set k = number of clauses.

A clique of size k must use exactly one vertex from each clause (vertices in
the same clause are never adjacent), and the pairwise non-contradiction
condition guarantees a consistent truth assignment.  Hence the formula is
satisfiable iff the graph has a clique of at least k vertices.

Edge cases:
  * No clauses -> n = 0, edges = [], k = 0 -> Clique says yes (k <= 0).
  * An empty clause contributes no vertex but still counts towards k, so the
    clique can never reach k -> no, matching the unsatisfiable empty clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertices[i] = (clause_index, literal)
    vertices: list[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)
    edges: list[list[int]] = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            # Same clause: never adjacent.
            # Complementary literals: never adjacent.
            if ci != cj and li != -lj:
                edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}
