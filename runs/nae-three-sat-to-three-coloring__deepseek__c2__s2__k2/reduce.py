"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Given a NAE-3-SAT instance {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
we build a graph {"n": n, "edges": [[u, v], ...]} that is 3-colourable
exactly when the formula is a yes-instance.

Construction
------------
There is a base triangle on vertices TRUE, FALSE, BASE.  Every proper
3-colouring must give these three vertices the three distinct colours; we
call those colours T, F and B.

For each variable v there are two literal vertices pos[v] and neg[v].
Both are joined to BASE, and pos[v] is joined to neg[v].  Hence pos[v] and
neg[v] must receive the two colours other than B, i.e. one is T and the
other is F.  Reading pos[v] == T as "v is true" turns any colouring into a
truth assignment.

For each clause there is a triangle of three fresh vertices, one joined to
the literal vertex of each of the clause's three literals.  A clause
triangle needs all three colours.  If all three literals were true (all T)
then each clause vertex would be forbidden T and only F, B would remain,
which cannot colour a triangle; symmetrically for all false.  If the clause
has at least one true and at least one false literal, the triangle can be
coloured (the two vertices attached to T-literals take F and B, and the
vertex attached to the F-literal takes T, or the symmetric assignment).
Thus a 3-colouring exists iff every clause is not-all-equal.

A formula with no clauses is always yes, and is mapped to the empty graph,
which is trivially 3-colourable.
"""


def reduce(instance):
    """Return a 3-Coloring instance equivalent to the NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: NAE-3-SAT is yes for every m, including m = 0.
    # The empty graph is yes for 3-Coloring.
    if not clauses:
        return {"n": 0, "edges": []}

    # Base triangle: vertices 0, 1, 2.
    TRUE, FALSE, BASE = 0, 1, 2
    edges = [
        [TRUE, FALSE],
        [TRUE, BASE],
        [FALSE, BASE],
    ]

    # One pair of literal vertices per variable.
    pos = {}
    neg = {}
    next_vertex = 3
    for var in range(1, num_vars + 1):
        pos[var] = next_vertex
        neg[var] = next_vertex + 1
        next_vertex += 2

        # Both literal vertices touch BASE, so they cannot use colour B;
        # the edge between them then forces one to be T and the other F.
        edges.append([pos[var], neg[var]])
        edges.append([pos[var], BASE])
        edges.append([neg[var], BASE])

    # One triangle per clause, attached to the three literal vertices.
    for clause in clauses:
        triangle = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3

        edges.append([triangle[0], triangle[1]])
        edges.append([triangle[1], triangle[2]])
        edges.append([triangle[0], triangle[2]])

        for literal, clause_vertex in zip(clause, triangle):
            var = abs(literal)
            literal_vertex = pos[var] if literal > 0 else neg[var]
            edges.append([literal_vertex, clause_vertex])

    return {"n": next_vertex, "edges": edges}
