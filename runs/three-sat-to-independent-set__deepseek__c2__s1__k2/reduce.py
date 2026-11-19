"""Polynomial-time reduction from 3-SAT (ThreeSat) to Independent Set.

Construction
------------
For a 3-SAT instance with m variables and c clauses:

* Create one vertex for every literal occurrence in every clause.
  Clause i (0-indexed) with literals [l0, l1, l2] gets vertices
  3*i, 3*i+1, 3*i+2.
* Within each clause, connect every pair of its vertices (a clique).
  This enforces that an independent set can contain at most one literal
  from each clause.
* For every variable v, connect every vertex whose literal is +v to
  every vertex whose literal is -v.  This enforces consistency: we may
  not simultaneously "choose" v and -v.
* Set k = number of clauses.

Correctness
-----------
(=>) Given a satisfying assignment, pick, in each clause, one literal
that is true (exists by satisfaction).  Chosen vertices are pairwise
non-adjacent: no two come from the same clause (only one per clause),
and no two are complementary (the assignment cannot make both v and -v
true).  Hence they form an independent set of size c = k.

(<=) An independent set of size at least k must have size exactly k,
since each clause is a clique and contributes at most one vertex, so
there are at most c = k vertices.  Thus it contains exactly one vertex
per clause.  Assign each variable the truth value that makes its chosen
literal true; this is well defined because complementary literals are
adjacent, so the set never chooses both v and -v.  Every clause then
contains a true literal, so the formula is satisfiable.

The construction uses O(c) vertices and O(c^2) edges, so it runs in
polynomial time.
"""

from collections import defaultdict


def reduce(instance):
    """Reduce a ThreeSat instance to an IndependentSet instance."""
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # One vertex per literal occurrence.
    vertices = []          # vertex index -> literal
    clause_vertices = []   # clause index -> list of vertex indices
    idx = 0
    for clause in clauses:
        vs = []
        for lit in clause:
            vs.append(idx)
            vertices.append(lit)
            idx += 1
        clause_vertices.append(vs)

    n = idx
    edges = []
    edge_set = set()

    def add_edge(u, v):
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in edge_set:
            edge_set.add(key)
            edges.append([key[0], key[1]])

    # Clique among the literals of each clause: at most one per clause.
    for vs in clause_vertices:
        for a in range(len(vs)):
            for b in range(a + 1, len(vs)):
                add_edge(vs[a], vs[b])

    # Edges between complementary literals: cannot pick both v and -v.
    lit_to_vertices = defaultdict(list)
    for v, lit in enumerate(vertices):
        lit_to_vertices[lit].append(v)

    for lit, vs in lit_to_vertices.items():
        comp = -lit
        if comp in lit_to_vertices:
            for u in vs:
                for w in lit_to_vertices[comp]:
                    add_edge(u, w)

    return {"n": n, "edges": edges, "k": num_clauses}
