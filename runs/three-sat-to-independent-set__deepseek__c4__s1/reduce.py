"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (standard):
  * For every clause c and each of its 3 literals, create one vertex.
    Vertices are numbered clause by clause: clause i, literal j -> 3*i + j.
  * Inside each clause, connect all pairs of its 3 vertices (a triangle),
    so an independent set can use at most one vertex per clause.
  * For every pair of vertices whose literals are complementary (v and -v),
    add an edge, so an independent set cannot select both.
  * Set k = number of clauses.

A satisfying assignment gives one true literal per clause; the corresponding
vertices form an independent set of size (#clauses).  Conversely an
independent set of size (#clauses) must pick exactly one vertex per clause
and cannot pick complementary literals, so setting those literals true
(consistently) satisfies every clause.

Edge cases: no clauses -> n = 0, edges = [], k = 0, which is yes (k <= 0).
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges = []
    seen = set()

    def add_edge(u: int, v: int) -> None:
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([key[0], key[1]])

    # literal -> list of vertex ids carrying that literal
    literal_vertices: dict[int, list[int]] = {}

    for i, clause in enumerate(clauses):
        base = 3 * i
        # triangle inside the clause
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)
        for j, lit in enumerate(clause):
            literal_vertices.setdefault(lit, []).append(base + j)

    # edges between complementary literals
    for lit, verts in literal_vertices.items():
        if lit > 0:
            continue
        for u in verts:
            for v in literal_vertices.get(-lit, ()):
                add_edge(u, v)

    return {"n": n, "edges": edges, "k": len(clauses)}
