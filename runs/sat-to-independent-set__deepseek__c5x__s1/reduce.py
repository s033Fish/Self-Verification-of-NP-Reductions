"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard "gadget per clause" reduction):

  * For every occurrence of a literal in a clause, create one vertex.
    Vertices are grouped by clause.
  * Within each clause, connect every pair of its vertices (a clique), so
    an independent set can pick at most one literal per clause.
  * For every variable v, connect every vertex labelled +v to every vertex
    labelled -v (a literal and its negation cannot both be chosen).
  * Set k = number of clauses.

An independent set of size k then selects exactly one literal per clause,
with no contradictory pair, which is precisely a satisfying assignment.
Conversely any satisfying assignment yields such an independent set.

Edge cases:
  * No clauses -> k = 0, and k <= 0 is always yes (satisfiable). Correct.
  * An empty clause contributes no vertex, so at most (#clauses - 1)
    vertices can be picked (each clause contributes at most one), hence no
    independent set of size k exists. Correct (unsatisfiable).
  * Duplicated literals / clauses and tautological clauses are handled
    naturally by the construction.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence, tagged with its clause.
    vertex_clause: list[int] = []
    vertex_lit: list[int] = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            vertex_clause.append(clause_index)
            vertex_lit.append(literal)

    n = len(vertex_lit)
    edge_set: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u != v:
            edge_set.add(frozenset((u, v)))

    # Cliques inside each clause.
    by_clause: dict[int, list[int]] = defaultdict(list)
    for idx, clause_index in enumerate(vertex_clause):
        by_clause[clause_index].append(idx)
    for indices in by_clause.values():
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                add_edge(indices[a], indices[b])

    # Contradiction edges between v and -v.
    by_lit: dict[int, list[int]] = defaultdict(list)
    for idx, literal in enumerate(vertex_lit):
        by_lit[literal].append(idx)
    for literal, indices in by_lit.items():
        for other in by_lit.get(-literal, []):
            for i in indices:
                add_edge(i, other)

    edges = [sorted(edge) for edge in edge_set]

    return {"n": n, "edges": edges, "k": len(clauses)}
