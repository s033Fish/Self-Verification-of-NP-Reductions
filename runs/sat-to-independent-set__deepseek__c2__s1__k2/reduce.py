"""Polynomial-time reduction from SAT to Independent Set.

Construction (the classic Karp reduction)
-----------------------------------------
Given a CNF formula with variables 1..m and clauses C_1..C_r:

* Create one vertex for every *occurrence* of a literal in a clause.
  Occurrences are kept separate, so a clause [1, 1] yields two distinct
  vertices and a repeated clause yields a fresh clique each time.
* Inside every clause, connect all pairs of its vertices (a clique).  This
  forbids choosing two literals from the same clause.
* For every variable v, connect every vertex whose literal is +v with every
  vertex whose literal is -v.  This forbids choosing both v and -v, i.e. it
  enforces a consistent truth assignment.
* Set k = number of clauses.

Correctness
-----------
If the formula is satisfiable, pick one true literal per clause.  The chosen
vertices are pairwise non-adjacent (one per clause, and no contradictory
pair), giving an independent set of size r = k.

Conversely, any independent set of size >= k must contain exactly one vertex
from each of the r clauses (at most one per clique, and there are r cliques).
The consistency edges guarantee the chosen literals are non-contradictory, so
setting them true is a well-defined assignment satisfying every clause.

Edge cases
----------
* No clauses: k = 0, and the empty graph always has an independent set of
  size 0, so the answer is yes, matching the satisfiable empty formula.
* An empty clause [] contributes no vertex, so no independent set can reach
  size k = r (at most r-1 vertices can be chosen), so the answer is no,
  matching the unsatisfiable empty clause.
* num_vars = 0 forces all clauses to be empty, handled above.

The construction is linear in the size of the formula, hence polynomial.
"""


def reduce(instance):
    """Map a SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    # Assign a vertex id to each literal occurrence, clause by clause.
    vertices = []  # vertex id -> literal
    clause_vertices = []  # clause index -> list of vertex ids
    next_id = 0
    for clause in clauses:
        ids = []
        for literal in clause:
            ids.append(next_id)
            vertices.append(literal)
            next_id += 1
        clause_vertices.append(ids)

    edges = set()

    def add_edge(u, v):
        if u == v:
            return
        edges.add((u, v) if u < v else (v, u))

    # Clique edges within each clause.
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                add_edge(ids[i], ids[j])

    # Consistency edges between opposite literals of the same variable.
    positive = {}
    negative = {}
    for vertex, literal in enumerate(vertices):
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
                add_edge(u, v)

    return {
        "n": next_id,
        "edges": [[u, v] for u, v in sorted(edges)],
        "k": len(clauses),
    }
