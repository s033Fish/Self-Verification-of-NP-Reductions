"""Polynomial-time reduction from SAT to Independent Set.

Construction
------------
Given a CNF formula with clauses C_1, ..., C_t:

* For every *occurrence* of a literal in a clause create one vertex.  So the
  vertices are partitioned into t groups, one group per clause (a clause with
  r literals contributes r vertices; an empty clause contributes none).
* Inside each group make a clique: any two vertices coming from the same
  clause are joined by an edge.  Hence an independent set can pick at most one
  vertex per clause.
* For every pair of vertices whose literals are complementary (v and -v) add
  an edge.  Hence an independent set can never pick two vertices that demand
  contradictory truth values.
* Set k = number of clauses t.

Correctness
-----------
(=>) A satisfying assignment makes at least one literal of every clause true.
Pick one such true literal per clause.  No two picked literals are
complementary (all are true under the assignment), so the chosen t vertices
form an independent set of size t = k.

(<=) An independent set of size >= k must have size exactly k (at most one
vertex per clause, and there are k clauses), so it contains exactly one vertex
per clause.  Assign every variable the truth value that makes its chosen
literal true; complementary literals are never both chosen, so this is
consistent.  Every clause then contains a true literal, so the formula is
satisfiable.

Edge cases
----------
* No clauses: n = 0, k = 0, and k <= 0 is a yes instance.  Correct.
* An empty clause: that clause contributes no vertex, so at most t-1 vertices
  can be chosen while k = t, hence no.  Correct.
* Duplicate literals / duplicate clauses / tautological clauses are all
  handled naturally (edges are de-duplicated).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # Assign a vertex to every literal occurrence.
    literals: list[int] = []          # literal of each vertex
    clause_groups: list[tuple[int, int]] = []  # [start, end) vertex range per clause
    n = 0
    for clause in clauses:
        start = n
        for literal in clause:
            literals.append(literal)
            n += 1
        clause_groups.append((start, n))

    edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Clique inside every clause group.
    for start, end in clause_groups:
        for u in range(start, end):
            for v in range(u + 1, end):
                add_edge(u, v)

    # Edges between complementary literals.
    for u in range(n):
        lu = literals[u]
        for v in range(u + 1, n):
            if lu == -literals[v]:
                add_edge(u, v)

    return {"n": n, "edges": edges, "k": len(clauses)}
