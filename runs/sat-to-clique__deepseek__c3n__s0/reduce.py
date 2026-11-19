"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (standard):
  * For every occurrence of a literal in a clause, create one vertex.
    Vertices are grouped by clause; a vertex remembers which clause it
    came from and which literal it represents.
  * Add an edge between two vertices iff they come from *different*
    clauses and their literals are not complementary (i.e. not x and -x).
  * Set k = number of clauses.

Correctness:
  (=>) A satisfying assignment picks, for every clause, at least one true
  literal. Choosing one such literal occurrence per clause yields k
  vertices from k distinct clauses; no two chosen literals are
  complementary because both are true under the assignment. Hence they
  are pairwise adjacent: a clique of size k.
  (<=) A clique of size k must contain vertices from k distinct clauses
  (vertices of the same clause are never adjacent), i.e. exactly one
  literal occurrence per clause. Since no two clique vertices are
  complementary, the assignment that sets each chosen literal true is
  consistent, and it satisfies every clause. Hence the formula is
  satisfiable.

Edge cases:
  * No clauses -> k = 0, and Clique is yes for k <= 0. Correct (SAT yes).
  * An empty clause contributes no vertices, so no clique can reach size
    k (which counts that clause), giving "no". Correct.
  * Repeated literals / repeated clauses / tautological clauses are all
    handled naturally by the per-occurrence construction.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to a Clique instance."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    vertices: list[tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    n = len(vertices)
    edges: list[list[int]] = []
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue
            if li == -lj:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}
