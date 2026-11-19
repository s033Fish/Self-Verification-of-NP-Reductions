"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Construction
------------
For a 3-SAT instance with ``num_vars = n`` and clauses ``C_1..C_m``:

* For every variable ``i`` (1..n) create a triangle on three vertices
  ``pos_i``, ``neg_i`` and ``y_i`` (all three pairwise adjacent).
  ``pos_i`` represents the literal ``+i`` and ``neg_i`` the literal ``-i``.
* For every clause create one vertex ``c_j`` and join it to the three
  literal-vertices of its literals.

The target instance uses ``k = n``.

Correctness
-----------
``y_i`` is adjacent only to ``pos_i`` and ``neg_i``, so any dominating set
must contain at least one vertex of every variable triangle, hence at least
``n`` vertices.  If a dominating set has exactly ``n`` vertices it contains
exactly one vertex per triangle and no clause vertex; therefore every clause
vertex must be dominated by one of its literal neighbours, i.e. the chosen
literals hit every clause.  Assigning the corresponding truth values (and
anything for the variables whose chosen vertex is ``y_i``) satisfies the
formula.  Conversely, if the formula is satisfiable, choosing the true
literal-vertex of every variable (``n`` vertices) dominates all triangles and
every clause vertex.  Hence the graph has a dominating set of size at most
``n`` iff the formula is satisfiable.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a ThreeSat instance to a DominatingSet instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Vertex numbering:
    #   pos_i = 3*(i-1), neg_i = 3*(i-1)+1, y_i = 3*(i-1)+2
    #   clause j = 3*num_vars + j
    def literal_vertex(literal):
        var = abs(literal)
        base = 3 * (var - 1)
        return base if literal > 0 else base + 1

    edges = []
    for i in range(1, num_vars + 1):
        pos = 3 * (i - 1)
        neg = pos + 1
        y = pos + 2
        edges.append([pos, neg])
        edges.append([neg, y])
        edges.append([y, pos])

    for j, clause in enumerate(clauses):
        c = 3 * num_vars + j
        for literal in clause:
            edges.append([c, literal_vertex(literal)])

    n = 3 * num_vars + len(clauses)
    return {"n": n, "edges": edges, "k": num_vars}
