"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard "clause-literal" gadget):

  * For every occurrence of a literal in a clause create one vertex.  So the
    total number of vertices is the total number of literal occurrences.
  * Inside each clause, put an edge between every pair of its literal
    vertices (a clique).  Hence an independent set can use at most one
    vertex per clause.
  * For every variable v, add an edge between every vertex labelled +v and
    every vertex labelled -v (contradiction edges).  Hence an independent set
    cannot contain two contradictory literals.

  Set k = number of clauses.

Correctness:
  (=>) Given a satisfying assignment, pick in every clause one literal that is
       true.  These picked vertices are pairwise non-adjacent: no two come from
       the same clause (clique edges) and no two are contradictory (both true
       under the same assignment).  This yields an independent set of size
       equal to the number of clauses = k.
  (<=) Given an independent set of size >= k, it contains at most one vertex
       per clause, so with k clauses it contains exactly one vertex per clause
       (and every clause must have at least one literal vertex, i.e. no empty
       clause).  The chosen literals are pairwise non-contradictory, so the
       assignment that makes each chosen literal true is well defined and
       satisfies every clause.  (Variables not appearing among the chosen
       literals may be assigned arbitrarily.)

Edge cases:
  * No clauses: k = 0 and n = 0, and k <= 0 is always yes.  Correct.
  * An empty clause contributes no vertices but still counts towards k, so no
    independent set can reach size k.  Correct (unsatisfiable).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    edges: list[list[int]] = []
    seen_edges: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        key = frozenset((u, v))
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append([u, v])

    n = 0
    # vertices[i] = list of vertex ids created for clause i
    clause_vertices: list[list[int]] = []

    for clause in clauses:
        ids = list(range(n, n + len(clause)))
        n += len(clause)
        clause_vertices.append(ids)

    # Clique edges inside each clause.
    for ids in clause_vertices:
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                add_edge(ids[a], ids[b])

    # Contradiction edges between opposite literals of the same variable.
    # Group vertices by the literal they represent.
    positive: dict[int, list[int]] = {}
    negative: dict[int, list[int]] = {}
    for clause, ids in zip(clauses, clause_vertices):
        for literal, vertex in zip(clause, ids):
            if literal > 0:
                positive.setdefault(literal, []).append(vertex)
            else:
                negative.setdefault(-literal, []).append(vertex)

    for var, pos_vertices in positive.items():
        for neg_vertex in negative.get(var, []):
            for pos_vertex in pos_vertices:
                add_edge(pos_vertex, neg_vertex)

    return {"n": n, "edges": edges, "k": len(clauses)}
