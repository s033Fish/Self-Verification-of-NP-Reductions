"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Standard Karp reduction:
  * For every clause create one vertex per literal in that clause
    (so 3 * (#clauses) vertices total).
  * Join two vertices with an edge iff they come from different clauses
    and their literals are not contradictory (i.e. not l and -l).
  * Set k = number of clauses.

A clique of size k must pick exactly one vertex from each clause (no two
vertices of the same clause are adjacent) and the chosen literals are
pairwise non-contradictory, so they form a satisfying assignment.  The
formula is satisfiable iff such a clique exists.
"""

from __future__ import annotations

from problems import Clique, ThreeSat


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Clique instance."""
    ThreeSat.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal, remembering which clause it belongs to.
    literals: list[int] = []
    clause_of: list[int] = []
    for ci, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            clause_of.append(ci)

    n = len(literals)

    edges: list[list[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if clause_of[i] == clause_of[j]:
                continue  # same clause: never adjacent
            if literals[i] == -literals[j]:
                continue  # contradictory literals: never adjacent
            edges.append([i, j])

    k = len(clauses)

    result = {"n": n, "edges": edges, "k": k}
    Clique.validate(result)
    return result
