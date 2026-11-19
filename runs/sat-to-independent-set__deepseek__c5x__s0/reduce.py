"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard):
  * One vertex per *occurrence* of a literal in the formula.
  * Within every clause, all its literal-vertices form a clique, so an
    independent set can pick at most one literal from each clause.
  * For every pair of vertices whose literals are complementary (v and -v),
    add an edge, so an independent set cannot pick both v and -v.
  * Set k = number of clauses.

Then the graph has an independent set of size >= k iff the formula is
satisfiable: size k forces exactly one literal per clause, and the
complementarity edges make the chosen literals a consistent assignment.
An empty clause contributes no vertex, so k can never be reached, matching
the "empty clause => unsatisfiable" rule.  A formula with no clauses gives
n = 0 and k = 0, which is a yes-instance (k <= 0).

The construction is polynomial: O(L^2) edges for L literal occurrences.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign a vertex id to every literal occurrence.
    literals: list[int] = []          # vertex id -> literal
    clause_vertices: list[list[int]] = []
    for clause in clauses:
        ids: list[int] = []
        for literal in clause:
            ids.append(len(literals))
            literals.append(literal)
        clause_vertices.append(ids)

    n = len(literals)
    edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Clique edges inside each clause.
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Edges between complementary literals.
    by_literal: dict[int, list[int]] = {}
    for vertex, literal in enumerate(literals):
        by_literal.setdefault(literal, []).append(vertex)
    for vertex, literal in enumerate(literals):
        for other in by_literal.get(-literal, ()):
            add_edge(vertex, other)

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}
