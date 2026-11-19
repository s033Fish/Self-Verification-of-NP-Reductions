"""Reduction from 3-SAT to Vertex Cover.

The source problem is ``ThreeSat`` with instances of the form

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains exactly
three literals on three distinct variables.

The target problem is ``VertexCover`` with instances of the form

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0 .. n-1`` and ``k`` is the size bound for the
cover.

We implement the classic polynomial‑time reduction (see, e.g., Garey &
Johnson, *Computers and Intractability*).  For each Boolean variable we create
two vertices – one representing the literal *x* and the other representing
its negation – and connect them by an edge.  Any vertex cover must contain at
least one endpoint of this edge, which corresponds to choosing a truth value
for the variable.

For each clause we create a triangle of three new vertices, each associated
with one literal of the clause.  The triangle forces the cover to pick at
least two of its three vertices.  Additionally, we connect each clause‑
literal vertex to the corresponding variable‑literal vertex (the true or
false vertex of that variable).  If a literal is set to true, the cover can
pick the clause‑literal vertex (covering the two triangle edges incident to
it) and rely on the variable vertex to cover the connecting edge, thereby
using only two vertices for the clause.  If the clause is unsatisfied, the
cover would need three vertices from the triangle, exceeding the budget.

Setting ``k = m + 2 * |C|`` (where ``|C|`` is the number of clauses) yields the
correct equivalence: the 3‑SAT instance is satisfiable iff the constructed
graph has a vertex cover of size at most ``k``.

The ``reduce`` function below builds this graph in linear time with respect
to the size of the 3‑SAT instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` representing the
        vertex‑cover instance equivalent to the given 3‑SAT formula.
    """
    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex numbering:
    #   for variable i (1‑based): true vertex = 2*(i-1), false vertex = 2*(i-1)+1
    #   clause vertices start after the 2*m variable vertices.
    var_true = lambda v: 2 * (v - 1)
    var_false = lambda v: 2 * (v - 1) + 1

    edges_set = set()

    # 1. Variable edges (force a choice between true/false)
    for v in range(1, m + 1):
        u = var_true(v)
        w = var_false(v)
        edges_set.add((min(u, w), max(u, w)))

    # 2. Clause gadgets
    clause_vertex_base = 2 * m
    for idx, clause in enumerate(clauses):
        base = clause_vertex_base + 3 * idx
        # triangle edges among the three clause vertices
        tri_edges = [(base, base + 1), (base + 1, base + 2), (base, base + 2)]
        for u, v in tri_edges:
            edges_set.add((min(u, v), max(u, v)))

        # connections from clause literal vertices to variable literal vertices
        for pos, lit in enumerate(clause):
            clause_vert = base + pos
            var = abs(lit)
            if lit > 0:
                var_vert = var_true(var)
            else:
                var_vert = var_false(var)
            edges_set.add((min(clause_vert, var_vert), max(clause_vert, var_vert)))

    # Convert edge set to list of [u, v]
    edges = [[u, v] for (u, v) in edges_set]

    n = clause_vertex_base + 3 * len(clauses)  # total number of vertices
    k = m + 2 * len(clauses)

    return {"n": n, "edges": edges, "k": k}

