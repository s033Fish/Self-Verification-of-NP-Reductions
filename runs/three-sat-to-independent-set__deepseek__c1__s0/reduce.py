"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction
------------
For each clause we create a triangle of three vertices, one for each literal
in the clause.  Any independent set can therefore contain at most one vertex
from each clause-triangle.

For every variable v we connect (with an edge) every vertex labelled by the
literal +v to every vertex labelled by the literal -v.  These "consistency"
edges prevent an independent set from choosing both v and -v.

Let k be the number of clauses.  A satisfying assignment yields an independent
set of size k: pick, in each clause-triangle, one vertex whose literal is true.
Conversely, an independent set of size k must contain exactly one vertex from
each triangle, and the consistency edges guarantee that the chosen literals do
not contain both v and -v for any variable; assigning each variable the sign of
the chosen literal (arbitrarily for unmentioned variables) satisfies every
clause.  Hence the graph has an independent set of size at least k iff the
formula is satisfiable.

Edge cases
----------
* No clauses: n = 0, k = 0, and Independent Set is yes because k <= 0.
* A clause may repeat; repeated clauses simply produce repeated triangles,
  which is harmless.
* Variables that never occur produce no consistency edges.
"""


def reduce(instance):
    """Return an Independent Set instance equivalent to the 3-SAT instance.

    Input format:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    edges = []

    # One triangle per clause: vertices 3*i, 3*i+1, 3*i+2.
    for i in range(num_clauses):
        a = 3 * i
        b = a + 1
        c = a + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

    # Collect vertices by literal sign, then connect opposite signs of the
    # same variable.  A clause uses three different variables, so a positive
    # and a negative occurrence of one variable are never in the same clause;
    # these edges are therefore distinct from the triangle edges.
    positive = {}
    negative = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            vertex = 3 * i + j
            if literal > 0:
                positive.setdefault(literal, []).append(vertex)
            else:
                negative.setdefault(-literal, []).append(vertex)

    for variable, pos_vertices in positive.items():
        for neg_vertex in negative.get(variable, ()):
            for pos_vertex in pos_vertices:
                edges.append([pos_vertex, neg_vertex])

    return {
        "n": 3 * num_clauses,
        "edges": edges,
        "k": num_clauses,
    }
