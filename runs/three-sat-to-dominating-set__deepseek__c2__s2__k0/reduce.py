"""Polynomial-time reduction from 3-SAT to Dominating Set.

Construction
------------
Let the 3-SAT instance have m variables and t clauses.

Vertices
  * For each variable v in 1..m create two vertices:
        T_v = 2*(v-1)      (literal  +v is true)
        F_v = 2*(v-1) + 1  (literal  -v is true)
    joined by the edge [T_v, F_v].
  * For each clause j in 0..t-1 create a vertex  C_j = 2*m + j.

Edges
  * [T_v, F_v] for every variable v.
  * [C_j, L] for every literal L occurring in clause j, where L is the
    vertex representing that literal (T_v for +v, F_v for -v).

Parameter
  k = m  (the number of variables).

Correctness
-----------
Every variable pair {T_v, F_v} needs at least one vertex of the pair in
any dominating set (no single other vertex is adjacent to both, because a
clause never contains both v and -v), so |D| >= m.  A dominating set of
size m therefore contains exactly one of T_v, F_v per variable, which
encodes an assignment.  The clause vertex C_j is dominated by a chosen
literal vertex iff that literal is true, so all clause vertices are
dominated iff the assignment satisfies every clause.  Hence a dominating
set of size at most m exists iff the formula is satisfiable.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    t = len(clauses)

    n = 2 * m + t
    edges = []

    # Variable gadget: one edge per variable.
    for v in range(m):
        edges.append([2 * v, 2 * v + 1])

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        c = 2 * m + j
        for lit in clause:
            var = abs(lit)
            base = 2 * (var - 1)
            if lit < 0:
                base += 1
            edges.append([c, base])

    return {"n": n, "edges": edges, "k": m}
