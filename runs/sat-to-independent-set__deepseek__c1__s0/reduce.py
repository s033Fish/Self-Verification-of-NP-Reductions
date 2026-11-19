"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction
------------
Given a CNF formula with clauses C_1, ..., C_k:

* Create one vertex for every *occurrence* of a literal in a clause.
  (Repeated literals therefore yield distinct vertices.)
* For each clause, add an edge between every pair of vertices coming from
  that clause, making the vertices of a clause a clique.  Hence an
  independent set can pick at most one literal occurrence per clause.
* For every variable v, add an edge between each vertex labelled +v and
  each vertex labelled -v.  Hence an independent set cannot pick both a
  variable and its negation.
* Set k = number of clauses.

An independent set of size k then corresponds exactly to choosing one
satisfied literal per clause without ever choosing both v and -v, i.e. to
a satisfying assignment.  Conversely a satisfying assignment yields such
an independent set.  An empty clause contributes no vertex and cannot be
covered, so the formula is unsatisfiable exactly when no independent set
of size k exists.  The formula with no clauses gives k = 0, which is
always a yes-instance.

The construction uses O(L^2) time and space for L total literal
occurrences, so it is polynomial.
"""


def reduce(instance):
    """Reduce a SAT instance to an Independent Set instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[literal, ...], ...]}``
    and the result is ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    clauses = instance["clauses"]

    edges = []
    seen = set()

    def add_edge(u, v):
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # One vertex per literal occurrence; remember each vertex's literal.
    literal_of = []
    clause_vertices = []
    for clause in clauses:
        vs = []
        for literal in clause:
            vs.append(len(literal_of))
            literal_of.append(literal)
        clause_vertices.append(vs)
        # Clique on the vertices of this clause.
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                add_edge(vs[i], vs[j])

    # Conflict edges between opposite literals of the same variable.
    by_literal = {}
    for vertex, literal in enumerate(literal_of):
        by_literal.setdefault(literal, []).append(vertex)
    for literal, vertices in by_literal.items():
        opposite = -literal
        if literal < opposite and opposite in by_literal:
            for u in vertices:
                for v in by_literal[opposite]:
                    add_edge(u, v)

    return {"n": len(literal_of), "edges": edges, "k": len(clauses)}
