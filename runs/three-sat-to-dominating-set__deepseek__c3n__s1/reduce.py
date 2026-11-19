"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Construction
------------
Let the formula have m = num_vars variables and c clauses.

Vertices:
  * For each variable v in 1..m create two vertices
        T_v = 2*(v-1)        (represents "v is true")
        F_v = 2*(v-1) + 1    (represents "v is false")
    joined by the edge (T_v, F_v).
  * For each clause j (0-based) create one vertex
        C_j = 2*m + j
    and connect it to the vertex of every literal occurring in the clause
    (positive literal v -> T_v, negative literal -v -> F_v).

So n = 2*m + c and the edge set is as above.

Set k = m.

Correctness
-----------
(=>) If the formula is satisfiable, choose for every variable the vertex of a
literal that is made true by the assignment.  That is m = k vertices.  Every
variable gadget edge has a chosen endpoint, so both of its vertices are
dominated.  Every clause is satisfied, hence its clause vertex is adjacent to
the chosen vertex of a true literal and is dominated.  So a dominating set of
size k exists.

(<=) Suppose D is a dominating set with |D| <= m.  For a variable v with no
vertex among {T_v, F_v} in D, both T_v and F_v must be dominated from outside
the gadget.  The only outside neighbours of T_v are clause vertices of clauses
containing v, and those of F_v are clause vertices of clauses containing -v;
these are distinct clause vertices, so at least two clause vertices of D are
needed for such a variable.  If p variables have no chosen vertex and q have
one, then |D| >= q + 2p = (m - p) + 2p = m + p, so |D| <= m forces p = 0.
Hence exactly one vertex per variable is in D (no room for clause vertices),
which defines an assignment, and every clause vertex is dominated, i.e. every
clause contains a true literal.  So the formula is satisfiable.

Edge cases
----------
m = 0, no clauses: n = 0, k = 0 -> n = 0 is yes for k >= 0, matching the
empty formula being satisfiable.  With no clauses k = m and n = 2m, so
k >= n only when m = 0, consistent.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Dominating Set instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 2 * num_vars + len(clauses)
    edges: list[list[int]] = []

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        true_vertex = 2 * (v - 1)
        false_vertex = 2 * (v - 1) + 1
        edges.append([true_vertex, false_vertex])

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        clause_vertex = 2 * num_vars + j
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                var_vertex = 2 * (var - 1)
            else:
                var_vertex = 2 * (var - 1) + 1
            edges.append([clause_vertex, var_vertex])

    return {"n": n, "edges": edges, "k": num_vars}
