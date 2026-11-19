"""Polynomial-time reduction from 3-Coloring to positive 1-in-3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[a, b, c], ...]}

Construction
------------
For every vertex v and colour k in {0, 1, 2} introduce a Boolean variable
c(v, k) meaning "vertex v receives colour k".

For every edge i = (u, v) and colour k introduce one auxiliary variable
t(i, k).

Clauses:
  * one clause [c(v,0), c(v,1), c(v,2)] per vertex, forcing exactly one
    colour on v;
  * one clause [c(u,k), c(v,k), t(i,k)] per edge i = (u,v) and colour k.
    This clause forbids c(u,k) and c(v,k) from both being true (if they
    were, at least two of its three variables would be true), while a
    suitable value of t(i,k) always exists whenever at most one of them
    is true.

Hence a satisfying assignment of the 1-in-3-SAT instance is exactly a
proper 3-colouring of the graph, and vice versa.  The construction uses
3n + 3|E| variables and n + 3|E| clauses, so it runs in polynomial time.
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        return {"num_vars": 0, "clauses": []}

    num_colour_vars = 3 * n
    num_vars = num_colour_vars + 3 * len(edges)

    def colour_var(vertex: int, colour: int) -> int:
        return 3 * vertex + colour + 1

    def edge_var(edge_index: int, colour: int) -> int:
        return num_colour_vars + 3 * edge_index + colour + 1

    clauses: list[list[int]] = []

    # Exactly one colour per vertex.
    for vertex in range(n):
        clauses.append([
            colour_var(vertex, 0),
            colour_var(vertex, 1),
            colour_var(vertex, 2),
        ])

    # Adjacent vertices may not share a colour.
    for edge_index, (u, v) in enumerate(edges):
        for colour in range(3):
            clauses.append([
                colour_var(u, colour),
                colour_var(v, colour),
                edge_var(edge_index, colour),
            ])

    return {"num_vars": num_vars, "clauses": clauses}
