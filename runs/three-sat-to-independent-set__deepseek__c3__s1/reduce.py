"""Polynomial-time reduction from 3-SAT (SOURCE) to Independent Set (TARGET).

Construction (standard clause/variable gadget reduction):

  * For every clause C_i = (l1, l2, l3) create a triangle of three vertices,
    one per literal occurrence.  Vertices 3*i, 3*i+1, 3*i+2 correspond to the
    three literals of clause i.  The three triangle edges forbid picking two
    literals from the same clause.
  * For every pair of literal occurrences (u, lu) and (v, lv) that lie in
    different clauses and are complementary (lu == -lv), add a "conflict"
    edge.  This forbids picking both v and -v.
  * Set k = number of clauses.

A satisfying assignment selects, for each clause, one true literal; the chosen
occurrences are pairwise non-adjacent (one per clause, no complementary pair),
so they form an independent set of size = #clauses.  Conversely any independent
set contains at most one vertex per triangle, hence at most #clauses vertices;
if it has #clauses vertices it picks exactly one literal per clause and no
complementary pair, which yields a satisfying assignment.

Edge case: a formula with no clauses reduces to n = 0, edges = [], k = 0,
which is a yes-instance of Independent Set (k <= 0), matching 3-SAT's yes.
"""

from problems import TARGET


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance."""
    clauses = instance["clauses"]

    edges = []
    # literal_of[v] = the literal (signed int) that vertex v represents.
    literal_of = []

    # One triangle per clause.
    for i, clause in enumerate(clauses):
        base = 3 * i
        for j, literal in enumerate(clause):
            literal_of.append(literal)
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    n = 3 * len(clauses)

    # Conflict edges between complementary literal occurrences.
    for u in range(n):
        for v in range(u + 1, n):
            if literal_of[u] == -literal_of[v]:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}


if __name__ == "__main__":
    TARGET.validate(reduce({"num_vars": 0, "clauses": []}))
    print("ok")
