"""Polynomial-time reduction from 3-Coloring (SOURCE) to SAT (TARGET).

Idea
----
Introduce a boolean variable x_{v,c} for every vertex v and colour c in {0,1,2},
meaning "vertex v receives colour c".  Number the variables as

    var(v, c) = 3 * v + c + 1        (so variables run 1..3n)

and build the CNF with the following clauses:

  * For every vertex v:
        [x_{v,0}, x_{v,1}, x_{v,2}]
    i.e. v gets at least one colour.

  * For every vertex v and every pair of distinct colours c < d:
        [-x_{v,c}, -x_{v,d}]
    i.e. v gets at most one colour.

  * For every edge {u, v} and every colour c:
        [-x_{u,c}, -x_{v,c}]
    i.e. the two endpoints of an edge do not share a colour.

A satisfying assignment of this formula is exactly a proper 3-colouring of the
graph (each vertex picks exactly one colour, adjacent vertices differ), and
conversely every proper 3-colouring yields a satisfying assignment.  The
formula has 3n variables and 4n + 3|E| clauses, so the construction is linear
in the size of the input.
"""

from __future__ import annotations


def _var(vertex: int, colour: int) -> int:
    """Variable (1-based) meaning 'vertex gets colour'."""
    return 3 * vertex + colour + 1


def reduce(instance):
    """Reduce a 3-Coloring instance to a SAT instance.

    Input : {"n": n, "edges": [[u, v], ...]}
    Output: {"num_vars": m, "clauses": [[literal, ...], ...]}
    """
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    for v in range(n):
        # At least one colour for v.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour for v.
        clauses.append([-_var(v, 0), -_var(v, 1)])
        clauses.append([-_var(v, 0), -_var(v, 2)])
        clauses.append([-_var(v, 1), -_var(v, 2)])

    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}
