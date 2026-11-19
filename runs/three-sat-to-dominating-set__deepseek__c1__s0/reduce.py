"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Let m = num_vars and let the clauses be C_0, ..., C_{c-1}.

For each variable v (1..m) create a triangle on three vertices:
    T_v = 3*(v-1)      (literal  +v)
    F_v = 3*(v-1) + 1  (literal  -v)
    D_v = 3*(v-1) + 2  (dummy)
with edges (T_v, F_v), (T_v, D_v), (F_v, D_v).

For each clause C_j create a vertex
    C_j = 3*m + j
and connect it to the literal vertex of each of its three literals
(+v -> T_v, -v -> F_v).

Set k = m.

Correctness
-----------
The dummy D_v is adjacent only to T_v and F_v, so every dominating set
must contain at least one of {T_v, F_v, D_v} for each variable; these sets
are disjoint, hence any dominating set has size >= m.

If a dominating set D has |D| <= m, it has exactly one vertex in each
triangle and none of the clause vertices.  Each clause vertex C_j must then
be adjacent to a chosen literal vertex, i.e. C_j contains that literal.
Interpreting a chosen T_v as "v true", a chosen F_v as "v false" and a
chosen D_v arbitrarily, every clause contains a true literal, so the
formula is satisfiable.

Conversely, given a satisfying assignment, pick for each variable the
vertex of its true literal (T_v or F_v).  These m vertices dominate every
triangle (the chosen vertex is adjacent to the other two) and every clause
vertex (each clause has a true literal, whose vertex is chosen and adjacent
to the clause vertex).  Hence a dominating set of size m exists.

Therefore the formula is satisfiable iff the graph has a dominating set of
size at most k = m.  The construction is clearly polynomial.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    n = 3 * num_vars + num_clauses
    edges = []

    # Variable gadgets: one triangle per variable.
    for v in range(num_vars):
        base = 3 * v
        edges.append([base, base + 1])      # T_v -- F_v
        edges.append([base, base + 2])      # T_v -- D_v
        edges.append([base + 1, base + 2])  # F_v -- D_v

    # Clause vertices connected to their literals.
    for j, clause in enumerate(clauses):
        clause_vertex = 3 * num_vars + j
        for lit in clause:
            var_index = abs(lit) - 1
            if lit > 0:
                literal_vertex = 3 * var_index       # T_v
            else:
                literal_vertex = 3 * var_index + 1   # F_v
            edges.append([clause_vertex, literal_vertex])

    return {"n": n, "edges": edges, "k": num_vars}
