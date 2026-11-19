"""Polynomial-time reduction from SAT (CNF satisfiability) to Clique.

Standard Karp reduction:

* One vertex per literal occurrence in the formula, grouped by the clause it
  comes from.  Repeated literals and repeated clauses simply produce more
  vertices / groups.
* Two vertices from *different* clause groups are joined by an edge unless
  their literals are complementary (i.e. one is ``v`` and the other ``-v``).
  Vertices inside the same group are never joined.
* ``k`` is the number of clauses.

A satisfying assignment yields a clique of size k: pick one true literal from
each clause; chosen literals are pairwise non-complementary, hence adjacent.
Conversely, a clique of size k must contain exactly one vertex per group
(no intra-group edges, and there are exactly k groups), and the chosen
literals are pairwise non-complementary, so setting each chosen literal true
gives a consistent assignment satisfying every clause.

Edge cases line up with the target's rules:

* No clauses  -> k = 0, which Clique answers yes (k <= 0).
* An empty clause [] contributes a group with no vertices, so no clique can
  reach k = number of clauses -> no, as required.
"""


def reduce(instance):
    """Reduce a SAT instance to a Clique instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    Returns ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    clauses = instance["clauses"]

    # Assign a vertex id to every literal occurrence, remembering the clause
    # group it belongs to and the literal value itself.
    vertex_literal = []   # vertex id -> literal
    vertex_group = []     # vertex id -> clause index

    for group_index, clause in enumerate(clauses):
        for literal in clause:
            vertex_literal.append(literal)
            vertex_group.append(group_index)

    n = len(vertex_literal)

    # Join vertices from different groups unless their literals are
    # complementary.  Emitting [u, v] with u < v keeps the edge list
    # duplicate-free and canonical.
    edges = []
    for u in range(n):
        lit_u = vertex_literal[u]
        group_u = vertex_group[u]
        for v in range(u + 1, n):
            if vertex_group[v] == group_u:
                continue
            if lit_u == -vertex_literal[v]:
                continue
            edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}
