"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Construction (standard Karp reduction):
  * For every clause occurrence we create one group of 3 vertices, one vertex
    per literal in that clause.
  * Two vertices are joined by an edge iff they come from different clause
    groups and their literals are not complementary (not x and -x).
  * k = number of clause occurrences.

Correctness:
  (=>) A satisfying assignment makes at least one literal true in each clause.
       Choosing one such true literal per clause yields one vertex per group;
       no two chosen literals are complementary (both are true), so all chosen
       vertices are pairwise adjacent: a clique of size #clauses = k.
  (<=) A clique of size k must contain exactly one vertex from each group
       (there are k groups and no intra-group edges). The chosen literals are
       pairwise non-complementary, hence the assignment that sets each chosen
       literal to true is consistent and satisfies every clause.

Edge case: no clauses -> n = 0, edges = [], k = 0, which is a yes-instance of
Clique (k <= 0), matching the yes-instance of 3-SAT with no clauses.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    clauses = instance["clauses"]

    # vertices[i] is the list of 3 literal-vertices for clause i.
    vertices = []
    for clause in clauses:
        vertices.append(list(clause))

    n = 3 * len(clauses)

    # Assign a global index to every vertex and remember (clause_id, literal).
    index_of = []  # index_of[c][j] = vertex id
    literal_of = []  # literal_of[vertex id] = literal
    for c, clause in enumerate(vertices):
        row = []
        for lit in clause:
            row.append(len(literal_of))
            literal_of.append(lit)
        index_of.append(row)

    edges = []
    for c1 in range(len(vertices)):
        for c2 in range(c1 + 1, len(vertices)):
            for i in index_of[c1]:
                for j in index_of[c2]:
                    if literal_of[i] + literal_of[j] != 0:  # not complementary
                        edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}
