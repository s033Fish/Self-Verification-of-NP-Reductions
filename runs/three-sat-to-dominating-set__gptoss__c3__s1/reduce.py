"""Reduction from 3‑SAT to Dominating Set.

The classic reduction uses a variable gadget (two vertices T_i and F_i linked by an
edge) and a clause gadget consisting of a single vertex that is adjacent to the
three literal vertices representing the literals of the clause.  Setting k = m
forces any dominating set of size ≤ k to pick exactly one vertex from each
variable pair; such a set dominates a clause vertex iff the corresponding literal
is satisfied.  Hence the formula is satisfiable iff the graph has a dominating
set of size ≤ m.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, DominatingSet


def _add_edge(u: int, v: int, edge_set: set[tuple[int, int]]) -> None:
    """Add an undirected edge to *edge_set* with the smaller endpoint first."""
    if u == v:
        raise AssertionError("self-loop generated")
    if u > v:
        u, v = v, u
    edge_set.add((u, v))


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating‑Set instance.

    Returns a graph with ``n = 2*m + c`` vertices and ``k = m``.
    """
    # Validate source instance
    ThreeSat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c: int = len(clauses)

    # Variable vertices: for variable i (1‑based) true vertex = 2*(i‑1), false = 2*(i‑1)+1
    # Clause vertices start after the variable vertices.
    base_clause = 2 * m
    clause_vertex_ids: List[int] = [base_clause + i for i in range(c)]

    n = 2 * m + c
    edges: set[tuple[int, int]] = set()

    # Variable edges (T_i, F_i)
    for i in range(1, m + 1):
        t = 2 * (i - 1)
        f = t + 1
        _add_edge(t, f, edges)

    # Connect each clause vertex to the three literal vertices of the clause
    for idx, clause in enumerate(clauses):
        clause_v = clause_vertex_ids[idx]
        for literal in clause:
            var = abs(literal)
            lit_v = 2 * (var - 1) if literal > 0 else 2 * (var - 1) + 1
            _add_edge(clause_v, lit_v, edges)

    edge_list: List[List[int]] = [[u, v] for (u, v) in sorted(edges)]
    k = m  # one vertex per variable pair
    result: Dict[str, Any] = {"n": n, "edges": edge_list, "k": k}
    DominatingSet.validate(result)
    return result

