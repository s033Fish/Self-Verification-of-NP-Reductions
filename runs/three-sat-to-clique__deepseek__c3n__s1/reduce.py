"""Polynomial-time reduction from 3-SAT (ThreeSat) to Clique.

Standard reduction (Karp):
  * For every clause, create one vertex per literal in that clause.
  * Join two vertices with an edge iff they come from *different* clauses
    and their literals are not complementary (i.e. not v and -v).
  * Set k = number of clauses.

A satisfying assignment picks one true literal per clause; the chosen
literals come from distinct clauses and cannot contain a complementary
pair, so they form a clique of size k.  Conversely, a clique of size k
must pick exactly one vertex from each clause (vertices in the same
clause are never adjacent), and no two chosen literals are complementary,
so setting every chosen literal to true yields a satisfying assignment
(remaining variables arbitrary).
"""

from __future__ import annotations


def reduce(instance):
    """Map a 3-SAT instance to a Clique instance.

    instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    returns:  {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    # One vertex per (clause index, literal position).
    literals = []  # literals[i] = literal of vertex i
    clause_of = []  # clause_of[i] = clause index of vertex i
    for ci, clause in enumerate(clauses):
        for lit in clause:
            literals.append(lit)
            clause_of.append(ci)

    n = len(literals)

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            # Vertices in the same clause are never adjacent.
            if clause_of[i] == clause_of[j]:
                continue
            # Complementary literals are never adjacent.
            if literals[i] == -literals[j]:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}
