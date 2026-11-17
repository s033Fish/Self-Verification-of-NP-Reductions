"""Polynomial-time reduction from 3-Coloring to SAT.

Encoding (standard):
  * Variable x_{v,c} (1 <= v <= n, c in {0,1,2}) means "vertex v has colour c".
    Numbering: var(v, c) = 3*v + c + 1, so variables are 1..3n.
  * For every vertex v:            (x_{v,0} v x_{v,1} v x_{v,2})   at least one colour
  * For every v and c < d:         (-x_{v,c} v -x_{v,d})           at most one colour
  * For every edge {u,w} and colour c: (-x_{u,c} v -x_{w,c})       endpoints differ

A satisfying assignment of the CNF corresponds exactly to a proper
3-colouring, and vice versa.  The formula has O(n + |E|) clauses, each of
constant size, so the reduction is polynomial time.
"""

from __future__ import annotations


def _var(v: int, c: int) -> int:
    """Variable (1-indexed) for 'vertex v has colour c'."""
    return 3 * v + c + 1


def reduce(instance):
    """Reduce a 3-Coloring instance to a SAT instance.

    instance: {"n": n, "edges": [[u, v], ...]}
    returns:  {"num_vars": 3*n, "clauses": [...]}
    """
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    for v in range(n):
        # At least one colour.
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # At most one colour.
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-_var(v, c), -_var(v, d)])

    for u, w in edges:
        # Adjacent vertices must not share a colour.
        for c in range(3):
            clauses.append([-_var(u, c), -_var(w, c)])

    return {"num_vars": num_vars, "clauses": clauses}
