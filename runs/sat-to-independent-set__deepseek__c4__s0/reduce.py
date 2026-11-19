"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard):
  * One vertex for every literal occurrence in the formula (clauses are
    flattened; repeated literals become distinct vertices).
  * For every clause, all its literal-vertices form a clique, so an
    independent set can pick at most one literal per clause.
  * For every pair of vertices whose literals are complementary (v and -v),
    add an edge, so an independent set cannot pick contradictory literals.
  * k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking one true literal per clause.  Conversely any independent set of size
#clauses picks exactly one literal per clause with no contradictions, giving
a satisfying assignment.  Empty clauses contribute no vertex, so k exceeds
the number of vertices and the answer is "no", matching unsatisfiability.
"""

from collections import defaultdict


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    literals = []          # vertex index -> literal
    clause_vertices = []   # clause index -> list of vertex indices
    for clause in clauses:
        idxs = []
        for lit in clause:
            idxs.append(len(literals))
            literals.append(lit)
        clause_vertices.append(idxs)

    edges = set()

    # Clique among the vertices of each clause.
    for idxs in clause_vertices:
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                edges.add(frozenset((idxs[a], idxs[b])))

    # Edges between complementary literals.
    by_var = defaultdict(list)
    for i, lit in enumerate(literals):
        by_var[abs(lit)].append(i)
    for idxs in by_var.values():
        pos = [i for i in idxs if literals[i] > 0]
        neg = [i for i in idxs if literals[i] < 0]
        for p in pos:
            for q in neg:
                edges.add(frozenset((p, q)))

    return {
        "n": len(literals),
        "edges": [list(e) for e in edges],
        "k": len(clauses),
    }
