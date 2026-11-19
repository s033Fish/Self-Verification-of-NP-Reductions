"""Polynomial-time reduction from SAT to Independent Set.

Construction (the standard one):

  * Create one vertex for every literal *occurrence* in the formula.
  * Inside each clause, join every pair of its literal-vertices with an
    edge (a clique), so an independent set can pick at most one literal
    from each clause.
  * For every variable v, join every occurrence of +v to every occurrence
    of -v, so an independent set can never contain contradictory literals.
  * Set k = number of clauses.

Correctness:

  (=>) Given a satisfying assignment, pick one true literal from each
  clause.  These picks come from distinct clauses (hence no within-clause
  edge) and are all true under one assignment (hence no consistency edge),
  so they form an independent set of size k.

  (<=) An independent set of size k must pick exactly one vertex from each
  of the k clauses (at most one per clause because each clause is a clique,
  and there are only k clauses).  The consistency edges guarantee the
  chosen literals are non-contradictory, so setting each chosen literal
  true (and the remaining variables arbitrarily) satisfies every clause.

Edge cases:

  * No clauses: n = 0 and k = 0, and k <= 0 is a yes instance, matching
    the satisfiable empty formula.
  * An empty clause contributes no vertex, so at most (number of nonempty
    clauses) < k vertices can be chosen: the target is a no instance,
    matching the unsatisfiable empty clause.
  * Repeated literals / repeated clauses / clauses with v and -v are all
    handled naturally because vertices are per occurrence and edges are
    de-duplicated with a set.
"""


def reduce(instance):
    """Map a SAT instance to an Independent Set instance (same yes/no)."""
    clauses = instance["clauses"]

    edges = set()
    n = 0
    # occurrences[literal] = list of vertex ids created for that literal
    occurrences = {}

    for clause in clauses:
        start = n
        for literal in clause:
            occurrences.setdefault(literal, []).append(n)
            n += 1
        # Clique among all vertices of this clause.
        for i in range(start, n):
            for j in range(i + 1, n):
                edges.add((i, j))

    # Consistency edges: every +v occurrence joined to every -v occurrence.
    for literal, verts in occurrences.items():
        if literal > 0:
            for u in verts:
                for v in occurrences.get(-literal, ()):
                    edges.add((u, v) if u < v else (v, u))

    edge_list = [[u, v] for (u, v) in sorted(edges)]
    return {"n": n, "edges": edge_list, "k": len(clauses)}
