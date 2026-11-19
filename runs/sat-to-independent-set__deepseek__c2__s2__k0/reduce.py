"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (standard):
  * For every occurrence of a literal in a clause create one vertex.
  * Within each clause, all its literal-occurrence vertices form a clique.
    Hence an independent set contains at most one vertex per clause.
  * For every variable v, connect every occurrence of literal +v to every
    occurrence of literal -v (consistency edges).  Hence an independent set
    never contains both v and -v.
  * Set k = number of clauses.

An independent set of size k must choose exactly one vertex from each clause
clique, and the consistency edges guarantee the chosen literals are not
contradictory; assigning each variable accordingly (arbitrary if unused)
satisfies every clause.  Conversely, from a satisfying assignment choose one
true literal per clause; these vertices are pairwise non-adjacent, giving an
independent set of size k.  An empty clause contributes no vertex, so the
clique for it is empty and no independent set can reach k, matching the fact
that the formula is unsatisfiable.
"""

from typing import Any


def reduce(instance: dict) -> dict:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertex_of[i] is the literal for the i-th literal occurrence, in order.
    vertex_of = []
    clause_vertices = []
    for clause in clauses:
        current = []
        for literal in clause:
            current.append(len(vertex_of))
            vertex_of.append(literal)
        clause_vertices.append(current)

    n = len(vertex_of)
    edges = set()

    def add_edge(u: int, v: int) -> None:
        if u != v:
            edges.add(frozenset((u, v)))

    # Clique edges inside each clause.
    for current in clause_vertices:
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                add_edge(current[i], current[j])

    # Consistency edges between opposite literals of the same variable.
    positive = [[] for _ in range(num_vars + 1)]
    negative = [[] for _ in range(num_vars + 1)]
    for vertex, literal in enumerate(vertex_of):
        if literal > 0:
            positive[literal].append(vertex)
        else:
            negative[-literal].append(vertex)

    for var in range(1, num_vars + 1):
        for u in positive[var]:
            for v in negative[var]:
                add_edge(u, v)

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": len(clauses),
    }
