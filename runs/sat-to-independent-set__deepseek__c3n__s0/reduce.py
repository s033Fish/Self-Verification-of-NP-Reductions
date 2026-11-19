"""Polynomial-time reduction from SAT to Independent Set.

Standard reduction (Karp):

For a CNF formula with clauses C_1..C_p over variables 1..m:

* Create one vertex for every literal *occurrence* in the formula.  Two
  occurrences of the same literal in the same clause are distinct vertices.
* Within each clause, add an edge between every pair of its vertices (a
  clique).  A set may therefore contain at most one vertex per clause.
* For every variable v, add an edge between every vertex labelled v and
  every vertex labelled -v (consistency edges).  A set may therefore not
  contain both a literal and its negation.
* Set k = number of clauses.

A satisfying assignment picks exactly one true literal per clause; those
vertices form an independent set of size p (no two chosen literals are in
the same clause, and no two are contradictory).  Conversely, any independent
set of size p contains exactly one vertex per clause (cliques) and is
consistent (consistency edges); setting each variable according to the
chosen literal satisfies every clause.  Hence the answer is preserved.

Edge cases fall out automatically:
* No clauses  -> k = 0, and k <= 0 is always yes (formula is satisfiable).
* Empty clause -> that clause contributes no vertex, so no independent set
  can reach k = p; the target answers no, matching the source.
* Repeated literals / clauses containing both v and -v are handled by the
  clique edges; duplicate edges are removed.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign a unique vertex id to each literal occurrence.
    vertices: list[int] = []          # vertex id -> literal value
    clause_vertices: list[list[int]] = []
    next_id = 0
    for clause in clauses:
        ids = []
        for literal in clause:
            vertices.append(literal)
            ids.append(next_id)
            next_id += 1
        clause_vertices.append(ids)

    n = next_id
    edges: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u != v:
            edges.add(frozenset((u, v)))

    # Clique inside every clause.
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Consistency edges between v and -v for each variable.
    by_var: dict[int, list[int]] = {}
    for vid, literal in enumerate(vertices):
        by_var.setdefault(abs(literal), []).append(vid)

    for var, vids in by_var.items():
        positives = [vid for vid in vids if vertices[vid] > 0]
        negatives = [vid for vid in vids if vertices[vid] < 0]
        for p in positives:
            for q in negatives:
                add_edge(p, q)

    return {
        "n": n,
        "edges": [sorted(e) for e in edges],
        "k": len(clauses),
    }
