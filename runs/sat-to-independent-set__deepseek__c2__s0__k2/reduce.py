"""Polynomial-time reduction from SAT to Independent Set.

Construction (the standard clause/contradiction gadget):

* For every occurrence of a literal in a clause, create one vertex.
* Within each clause, connect every pair of its vertices (a clique), so an
  independent set can pick at most one literal per clause.
* For every variable v, connect every vertex holding literal +v to every
  vertex holding literal -v, so an independent set cannot pick both a
  variable and its negation.
* Set k equal to the number of clauses.

A satisfying assignment selects one true literal per clause; the selected
vertices form an independent set of size (number of clauses).  Conversely,
an independent set of that size picks exactly one literal per clause, and
the contradiction edges guarantee a consistent assignment satisfying all
clauses.  Empty clauses contribute no vertex, so any formula containing one
has maximum independent set strictly below k, as required.
"""

from itertools import combinations


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign a vertex to every literal occurrence.
    literal_of = []          # vertex -> literal
    clause_vertices = []     # clause index -> list of vertices
    for clause in clauses:
        vertices = []
        for literal in clause:
            vertices.append(len(literal_of))
            literal_of.append(literal)
        clause_vertices.append(vertices)

    n = len(literal_of)
    edges = set()

    # Clause cliques: at most one literal per clause.
    for vertices in clause_vertices:
        for u, v in combinations(vertices, 2):
            edges.add(frozenset((u, v)))

    # Contradiction edges: cannot choose v and -v together.
    positive = {}
    negative = {}
    for vertex, literal in enumerate(literal_of):
        if literal > 0:
            positive.setdefault(literal, []).append(vertex)
        else:
            negative.setdefault(-literal, []).append(vertex)
    for var, pos in positive.items():
        neg = negative.get(var)
        if not neg:
            continue
        for u in pos:
            for v in neg:
                edges.add(frozenset((u, v)))

    return {
        "n": n,
        "edges": [sorted(edge) for edge in edges],
        "k": len(clauses),
    }
