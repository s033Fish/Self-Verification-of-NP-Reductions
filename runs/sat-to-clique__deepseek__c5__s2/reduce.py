"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction:
  * For every clause i and every literal occurrence l in that clause, create a
    vertex (i, l).
  * Join two vertices (i, l) and (j, l') with an edge iff i != j and the
    literals l and l' are not complementary (i.e. not l == -l').
  * Set k = number of clauses.

Why it works:
  * A satisfying assignment lets us pick one true literal per clause; the
    chosen vertices lie in distinct clauses and no two are complementary, so
    they form a clique of size k.
  * A clique of size k must contain exactly one vertex from each clause (no
    edge joins two vertices of the same clause), and contains no complementary
    pair, so setting every chosen literal true is a consistent assignment that
    satisfies every clause.
  * A clause with no literals contributes no vertex, so k can never be reached
    (correctly "no").  A formula with no clauses gives k = 0, which is always
    "yes" for Clique.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to a Clique instance (both plain dicts)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertices[i] = (clause_index, literal)
    vertices: list[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for literal in clause:
            vertices.append((ci, literal))

    edges: list[list[int]] = []
    n = len(vertices)
    for a in range(n):
        ca, la = vertices[a]
        for b in range(a + 1, n):
            cb, lb = vertices[b]
            if ca != cb and la != -lb:
                edges.append([a, b])

    return {"n": n, "edges": edges, "k": len(clauses)}
