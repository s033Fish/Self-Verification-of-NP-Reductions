"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Construction (standard "literal occurrence" reduction)
------------------------------------------------------
Given a CNF formula with clauses C_0, ..., C_{p-1} over variables 1..m:

  * Create one graph vertex for every literal *occurrence* in the formula
    (so repeated literals and repeated clauses simply create more vertices).
  * Join two vertices with an edge iff they come from *different* clauses and
    their literals are not complementary (i.e. not x and -x).
  * Set k = p, the number of clauses.

Correctness
-----------
A clique can contain at most one vertex per clause (vertices of the same
clause are never adjacent), so a clique has size at most p.

(=>) If the formula is satisfiable, pick in each clause a literal that is
true under a satisfying assignment.  These p literals live in distinct
clauses and are pairwise non-complementary, hence they form a p-clique.

(<=) A p-clique picks exactly one vertex per clause.  Its literals are
pairwise non-complementary, so the assignment that sets a variable true if
some chosen literal is +v and false if some chosen literal is -v is
well defined; every chosen literal is then true, so every clause is
satisfied.

Edge cases
----------
  * No clauses: p = 0, so k = 0 and the empty graph is returned; k <= 0 is
    always a yes-instance, matching the empty formula being satisfiable.
  * An empty clause [] contributes no vertex, so no p-clique can exist
    (k = p > n), matching unsatisfiability.
  * k is never negative here, and the reduction is clearly polynomial.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a SAT instance to a Clique instance (both plain dicts)."""
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its clause index.
    literals = []          # literal of each vertex
    clause_of = []         # clause index of each vertex
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            clause_of.append(clause_index)

    n = len(literals)
    edges = []
    for i in range(n):
        li = literals[i]
        ci = clause_of[i]
        for j in range(i + 1, n):
            # Different clauses and not complementary literals.
            if ci != clause_of[j] and li != -literals[j]:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": len(clauses)}
