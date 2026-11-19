"""Polynomial-time reduction from 3-SAT to Clique.

Standard reduction (Karp): for every clause create one vertex per literal.
Two vertices are joined by an edge iff they come from different clauses and
their literals are not complementary (i.e. not x and -x).  A clique of size
equal to the number of clauses selects one literal per clause, and pairwise
compatibility means no variable is forced both true and false, so the chosen
literals can be extended to a satisfying assignment.  Conversely a satisfying
assignment lets us pick a true literal in each clause, giving such a clique.

For a formula with no clauses we return the empty graph with k = 0, which is
a yes-instance of Clique (k <= 0 is always yes), matching the satisfiability
of the empty formula.
"""


def reduce(instance):
    clauses = instance["clauses"]

    # One vertex per literal occurrence, grouped by clause.
    # Vertex 3*c + i corresponds to clause c, literal i.
    vertices = []
    for c, clause in enumerate(clauses):
        for i, literal in enumerate(clause):
            vertices.append((c, literal))

    n = len(vertices)

    edges = []
    for a in range(n):
        clause_a, lit_a = vertices[a]
        for b in range(a + 1, n):
            clause_b, lit_b = vertices[b]
            if clause_a == clause_b:
                continue
            # Compatible unless the literals are complementary.
            if lit_a == -lit_b:
                continue
            edges.append([a, b])

    return {"n": n, "edges": edges, "k": len(clauses)}
