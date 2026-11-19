"""Polynomial-time reduction from 3-SAT to Clique.

Standard reduction (Karp):
  * For every clause and every literal occurrence in it, create one vertex.
  * Join two vertices iff they belong to different clauses and their
    literals are not complementary (i.e. not x and -x).
  * Set k = number of clauses.

A clique of size k selects exactly one literal per clause, all pairwise
non-contradictory, which is exactly a satisfying assignment.  Conversely a
satisfying assignment yields such a clique.  A formula with no clauses maps
to k = 0, which is a yes-instance of Clique (clique of at least 0 vertices).
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # vertex_of[(clause_index, literal_index)] -> vertex id
    vertices = []          # (clause_index, literal)
    vertex_of = {}
    for ci, clause in enumerate(clauses):
        for li, literal in enumerate(clause):
            vertex_of[(ci, li)] = len(vertices)
            vertices.append((ci, literal))

    edges = []
    for a in range(len(vertices)):
        ca, la = vertices[a]
        for b in range(a + 1, len(vertices)):
            cb, lb = vertices[b]
            if ca == cb:
                continue
            if la == -lb:
                continue
            edges.append([a, b])

    return {"n": len(vertices), "edges": edges, "k": len(clauses)}
