"""Polynomial-time reduction from 3-SAT to Independent Set.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
For every clause C_i create a triangle on three new vertices, one per
literal occurrence in that clause.  Within a clause every pair of vertices
is joined by an edge, so an independent set contains at most one vertex
from each clause-triangle.

Additionally, for every two vertices in different clause-triangles whose
literals are complementary (one is +v and the other -v for the same
variable v), add an edge between them.  Such a pair cannot both be chosen,
which enforces consistency of the truth assignment represented by the
chosen literals.

Set k equal to the number of clauses.  Any independent set has at most one
vertex per triangle, hence size at most the number of clauses.  Therefore a
set of size at least k exists iff one literal can be selected from every
clause with no complementary pair selected, i.e. iff the formula is
satisfiable (variables that occur in no selected literal may be assigned
arbitrarily).

The graph has 3 * len(clauses) vertices and O(len(clauses)^2) edges, so the
construction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an Independent Set instance.

    The returned instance is yes for Independent Set exactly when the input
    is satisfiable.
    """
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Vertex 3*i + j corresponds to the j-th literal of clause i.
    n = 3 * num_clauses
    edges: list[list[int]] = []

    # Triangle inside each clause: at most one literal per clause may be
    # chosen.
    for i in range(num_clauses):
        base = 3 * i
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    # Conflict edges between complementary literals in different clauses.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for a in range(3):
                lit_a = clauses[i][a]
                u = 3 * i + a
                for b in range(3):
                    lit_b = clauses[j][b]
                    if lit_a == -lit_b:
                        v = 3 * j + b
                        edges.append([u, v])

    # One vertex per clause can be chosen; the assignment is satisfiable iff
    # that many mutually non-adjacent vertices exist.
    return {"n": n, "edges": edges, "k": num_clauses}
