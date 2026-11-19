"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction:
  * For each variable v in 1..m create two vertices, pos(v) and neg(v),
    joined by an edge (the variable gadget).
  * For each clause create one new vertex, joined to the three literal
    vertices of its literals.
  * Set k = m (number of variables).

Correctness:
  (<=) A satisfying assignment: put the true literal vertex of each
  variable in D.  The other vertex of each gadget is adjacent to it, so
  all gadget vertices are dominated, and every clause vertex is adjacent
  to at least one true literal.  |D| = m.
  (=>) Let D be a dominating set with |D| <= m.  For a variable v whose
  two literal vertices are both outside D, dominating pos(v) and neg(v)
  needs a clause vertex adjacent to each; no clause contains both v and
  -v, so these are two distinct clause vertices.  Hence if U is the set
  of variables with no literal in D, |D| >= (m-|U|) + 2|U| = m + |U|,
  forcing U empty.  So D has exactly one literal vertex per variable and
  no clause vertices, and every clause vertex must be adjacent to a
  chosen literal: the induced assignment satisfies every clause.
"""
from problems import SOURCE, TARGET


def reduce(instance):
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    def lit_index(lit):
        v = abs(lit)
        return 2 * (v - 1) + (0 if lit > 0 else 1)

    edges = []
    for v in range(1, m + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    next_vertex = 2 * m
    for clause in clauses:
        c = next_vertex
        next_vertex += 1
        for lit in clause:
            edges.append([c, lit_index(lit)])

    result = {"n": next_vertex, "edges": edges, "k": m}
    TARGET.validate(result)
    return result
