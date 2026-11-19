"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction
------------
For every literal occurrence in every clause we create one vertex.  The
vertices belonging to the same clause form a triangle, so an independent set
can pick at most one literal from each clause.  For every pair of vertices
whose literals are complementary (v and -v) we add an edge, so an independent
set may not pick both a variable and its negation.

The target instance asks for an independent set of size at least
k = number of clauses.  Any satisfying assignment yields such a set by picking
one true literal per clause (the triangles forbid two picks in one clause, and
the consistency edges forbid picking both v and -v).  Conversely, any
independent set of size k picks exactly one literal per clause and never both
a variable and its negation; setting those literals to true satisfies every
clause.

A formula with no clauses maps to the empty graph with k = 0, which is a yes
instance, matching the 3-SAT edge case.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    edges = set()
    vertex = 0
    # vertex -> literal it represents
    literals = []

    for clause in clauses:
        base = vertex
        for literal in clause:
            literals.append(literal)
            vertex += 1
        # Triangle on the three literal vertices of this clause.
        edges.add((base, base + 1))
        edges.add((base, base + 2))
        edges.add((base + 1, base + 2))

    # Consistency edges between complementary literals in different clauses.
    by_literal = {}
    for index, literal in enumerate(literals):
        by_literal.setdefault(literal, []).append(index)
    for literal, indices in by_literal.items():
        for other in by_literal.get(-literal, ()):
            for i in indices:
                for j in other:
                    if i != j:
                        edges.add((i, j) if i < j else (j, i))

    return {
        "n": vertex,
        "edges": [[u, v] for u, v in sorted(edges)],
        "k": len(clauses),
    }
