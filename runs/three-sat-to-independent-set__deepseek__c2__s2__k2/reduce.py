"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction
------------
For every clause we add one vertex per literal (3 vertices per clause).
Inside each clause the three vertices form a triangle, so an independent
set can pick at most one literal from each clause.

For every variable v we add an edge between every vertex labelled +v and
every vertex labelled -v (a complete bipartite graph between the positive
and negative occurrences of v).  Thus an independent set may not contain
two literals that contradict each other.

The target asks for an independent set of size at least k, where k is the
number of clauses.

Correctness
-----------
* If the formula is satisfiable, pick one true literal from each clause.
  These k vertices are pairwise non-adjacent: no two come from the same
  clause (one per clause) and no two are opposite literals of a variable
  (the assignment is consistent).  Hence there is an independent set of
  size k.
* If there is an independent set of size k, the triangle in each of the k
  clauses contributes at most one vertex, so the set contains exactly one
  literal from every clause.  Since it is independent, it never contains
  both v and -v for any variable, so setting exactly those chosen literals
  to true (and all other variables arbitrarily) satisfies every clause.

Edge cases
----------
* No clauses: n = 0, k = 0, and k <= 0 is yes, matching the empty formula
  being satisfiable.
* Repeated clauses simply produce repeated triangles, which is harmless.
* Variables that never occur produce no vertices or edges.

The construction is linear in the size of the input, hence polynomial.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One vertex per literal occurrence.
    n = 3 * len(clauses)

    edges = set()

    def add_edge(u, v):
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges.add((a, b))

    # Positive / negative occurrence vertices for each variable.
    positive = {v: [] for v in range(1, num_vars + 1)}
    negative = {v: [] for v in range(1, num_vars + 1)}

    for clause_index, clause in enumerate(clauses):
        base = 3 * clause_index
        # Triangle: at most one literal may be selected from a clause.
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)

        for offset, literal in enumerate(clause):
            vertex = base + offset
            variable = abs(literal)
            if literal > 0:
                positive[variable].append(vertex)
            else:
                negative[variable].append(vertex)

    # Conflict edges: cannot choose both v and -v.
    for variable in range(1, num_vars + 1):
        for u in positive[variable]:
            for v in negative[variable]:
                add_edge(u, v)

    return {
        "n": n,
        "edges": [list(edge) for edge in sorted(edges)],
        "k": len(clauses),
    }
