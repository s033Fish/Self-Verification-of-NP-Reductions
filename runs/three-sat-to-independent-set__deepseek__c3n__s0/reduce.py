"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction
------------
Given a 3-SAT instance with m variables and c clauses, build a graph:

  * For every clause i and every literal position j (0,1,2) create a vertex
    with index 3*i + j.  The three vertices of a clause form a triangle, so
    an independent set can pick at most one literal per clause.
  * For every pair of vertices whose literals are complementary (v and -v),
    add an edge.  This forbids picking both v and -v, i.e. it forbids
    contradictory truth assignments.

Set k = c (the number of clauses).

Correctness
-----------
(=>) If the formula is satisfiable, take a satisfying assignment and, for
each clause, pick one literal that is true under it (one vertex per clause).
No two picked vertices lie in the same triangle (one per clause) and no two
are complementary (both literals are true, so they cannot be v and -v).
Hence the picked set is independent and has size c = k.

(<=) If the graph has an independent set S with |S| >= k = c, then, since
each of the c triangles contributes at most one vertex, |S| = c and S
contains exactly one vertex from every triangle.  The complementary-literal
edges guarantee that S contains no pair v, -v, so we may set each variable
true if +v is in S, false if -v is in S, and arbitrarily otherwise.  Every
clause then has a true literal, so the formula is satisfiable.

Edge cases
----------
No clauses: c = 0, the graph has n = 0 vertices and k = 0.  k <= 0 is always
yes, matching the empty formula being satisfiable (for any m, including 0).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges: list[list[int]] = []

    # Triangle inside every clause.
    for i in range(len(clauses)):
        base = 3 * i
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])

    # Edges between complementary literals (any two clauses, including the
    # same clause -- though a clause never contains both v and -v).
    # literal -> list of vertex indices carrying it
    occurrences: dict[int, list[int]] = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            occurrences.setdefault(literal, []).append(3 * i + j)

    seen_pairs: set[tuple[int, int]] = set()
    for literal, vertices in occurrences.items():
        opposite = occurrences.get(-literal)
        if not opposite:
            continue
        for u in vertices:
            for v in opposite:
                a, b = (u, v) if u < v else (v, u)
                if (a, b) in seen_pairs:
                    continue
                seen_pairs.add((a, b))
                edges.append([a, b])

    return {"n": n, "edges": edges, "k": len(clauses)}
