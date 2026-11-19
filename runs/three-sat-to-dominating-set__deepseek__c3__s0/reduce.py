"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
For each variable i in 1..num_vars create a triangle on three fresh vertices:
    P_i  (stands for literal  +i)
    N_i  (stands for literal  -i)
    Y_i  (an auxiliary vertex that forces one of P_i / N_i to be chosen)

For each clause create one fresh vertex and connect it to the three vertices
that represent the clause's literals.

Set k = num_vars.

Why it works
------------
* Y_i is adjacent only to P_i and N_i, so any dominating set must contain at
  least one of {P_i, N_i, Y_i}.  The m triangles are vertex-disjoint, hence
  every dominating set has size >= m, and a dominating set of size <= m
  contains exactly one vertex per triangle and no clause vertex.
* A clause vertex is adjacent only to its three literal vertices, so it is
  dominated exactly when one of those literal vertices is in the set.
* (formula satisfiable => dominating set of size m)  Pick, for every variable,
  the vertex of the true literal.  This is one vertex per triangle (so it
  dominates all triangle vertices) and, because every clause has a true
  literal, every clause vertex is adjacent to a chosen vertex.
* (dominating set of size <= m => formula satisfiable)  As argued, the set has
  exactly one vertex per triangle.  Set variable i true if P_i is chosen and
  false if N_i is chosen (if Y_i is chosen the variable may be set either way,
  which is safe because Y_i is adjacent to no clause vertex).  Every clause
  vertex is dominated by one of its literal vertices, so that literal is true
  under the assignment; hence every clause is satisfied.

The construction uses 3*num_vars + len(clauses) vertices and
3*num_vars + 4*len(clauses) edges, so it runs in polynomial time.
"""


def reduce(instance):
    """Return a Dominating Set instance that is yes iff the 3-SAT instance is."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Literal -> vertex id.  Variable i (1-based) owns triangle vertices
    # 3*(i-1) = P_i, 3*(i-1)+1 = N_i, 3*(i-1)+2 = Y_i.
    def literal_vertex(literal):
        base = 3 * (abs(literal) - 1)
        return base if literal > 0 else base + 1

    edges = []
    for i in range(1, num_vars + 1):
        p, n, y = 3 * (i - 1), 3 * (i - 1) + 1, 3 * (i - 1) + 2
        edges.append([p, n])
        edges.append([n, y])
        edges.append([p, y])

    next_vertex = 3 * num_vars
    for clause in clauses:
        clause_vertex = next_vertex
        next_vertex += 1
        for literal in clause:
            edges.append([clause_vertex, literal_vertex(literal)])

    return {"n": next_vertex, "edges": edges, "k": num_vars}
