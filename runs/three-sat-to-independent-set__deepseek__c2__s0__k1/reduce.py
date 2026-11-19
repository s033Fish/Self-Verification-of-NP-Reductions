"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction (the classic "clause gadget" reduction):

  * For every clause c_i = (l1, l2, l3) create a triangle of three vertices
    v_{i,1}, v_{i,2}, v_{i,3}, one per literal.  Inside a triangle all three
    pairs are joined by edges, so an independent set can contain at most one
    vertex from each clause gadget.
  * For every variable x, join every vertex labelled +x to every vertex
    labelled -x.  This forbids choosing two literals that contradict each
    other.
  * Set k = number of clauses.

Why it is correct:

  (=>) A satisfying assignment makes at least one literal true in each
  clause.  Pick one such true literal per clause.  No two picked vertices
  lie in the same triangle (one per clause) and no two picked vertices
  contradict each other (the assignment is consistent), so the picked
  vertices form an independent set of size = number of clauses = k.

  (<=) An independent set has at most one vertex per clause gadget, so a set
  of size >= k = number of clauses contains exactly one vertex per clause.
  Assign each variable true iff its positive literal was picked (a variable
  cannot have both polarities picked because those vertices are adjacent).
  Every clause has one picked literal, which is therefore true, so the
  formula is satisfied.

The construction uses O(|clauses|) vertices and O(|clauses|^2) edges and is
computed in polynomial time.  No brute-force solver is used.
"""

from itertools import combinations


def reduce(instance):
    """Map a 3-SAT instance to an Independent Set instance.

    Input : {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance["clauses"]

    n = 3 * len(clauses)

    edges = set()

    def add_edge(u, v):
        if u != v:
            edges.add((u, v) if u < v else (v, u))

    # One triangle per clause: at most one chosen literal per clause.
    for i in range(len(clauses)):
        base = 3 * i
        for u, v in combinations(range(base, base + 3), 2):
            add_edge(u, v)

    # Join vertices carrying contradictory literals.
    # literal -> list of vertex ids for that literal
    by_literal = {}
    for i, clause in enumerate(clauses):
        for j, literal in enumerate(clause):
            by_literal.setdefault(literal, []).append(3 * i + j)

    for literal, verts in by_literal.items():
        opposite = by_literal.get(-literal)
        if opposite:
            for u in verts:
                for v in opposite:
                    add_edge(u, v)

    return {
        "n": n,
        "edges": [list(e) for e in sorted(edges)],
        "k": len(clauses),
    }
