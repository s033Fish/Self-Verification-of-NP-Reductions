"""Polynomial-time reduction from 3-SAT to Independent Set.

Standard reduction:
  * For every clause we create one vertex per literal (3 vertices), and we
    add the three edges forming a triangle among them.  An independent set can
    therefore pick at most one vertex (literal) per clause, and picking one
    means "this literal is the one that satisfies the clause".
  * For every pair of vertices whose literals are complementary (v and -v) we
    add an edge.  This forbids choosing both v and -v, i.e. it enforces a
    consistent truth assignment.
  * k = number of clauses.  A satisfying assignment yields an independent set
    of size (#clauses) by picking one true literal per clause; conversely an
    independent set of size (#clauses) picks exactly one literal per clause,
    no two complementary, so it defines a consistent assignment satisfying all
    clauses.

Edge cases:
  * No clauses: k = 0 and n = 0, and k <= 0 is always yes, matching the
    satisfiability of the empty formula (for any num_vars, including 0).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    clauses = instance["clauses"]

    edges: list[list[int]] = []
    # For each literal occurrence we store (vertex_id, variable, sign).
    occurrences: list[tuple[int, int, int]] = []

    next_vertex = 0
    for clause in clauses:
        base = next_vertex
        # Triangle among the three literals of the clause.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])
        for literal in clause:
            occurrences.append((next_vertex, abs(literal), 1 if literal > 0 else -1))
            next_vertex += 1

    # Edges between complementary literals (different variables can't clash,
    # and within a clause the variables are distinct so no complementary pair
    # occurs inside a triangle).
    by_var: dict[int, list[tuple[int, int]]] = {}
    for vertex, var, sign in occurrences:
        by_var.setdefault(var, []).append((vertex, sign))
    for var, entries in by_var.items():
        positives = [v for v, s in entries if s > 0]
        negatives = [v for v, s in entries if s < 0]
        for p in positives:
            for q in negatives:
                edges.append([p, q])

    n = next_vertex
    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}
