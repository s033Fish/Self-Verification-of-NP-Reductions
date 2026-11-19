"""Reduction from 3‑SAT to Dominating Set.

We use the classic reduction: for each variable i we create three vertices
forming a triangle: true_i, false_i, and a dummy vertex d_i.  Any dominating
set of size ≤ m must pick exactly one of true_i or false_i (picking the dummy
does not help dominate the clause vertices).  For each clause we add a vertex
c_j adjacent to the three literal vertices that would satisfy the clause.

If the formula is satisfiable, choose for each variable the true/false vertex
according to a satisfying assignment; these m vertices dominate all clause
vertices, and also dominate their own dummy vertices via the triangle edges.
Conversely, any dominating set of size ≤ m can contain at most one vertex from
each variable triangle, otherwise we would exceed the budget.  To dominate the
clause vertices, at least one incident literal vertex must be chosen, which
gives a satisfying assignment.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict with keys "num_vars" and "clauses" as defined by ThreeSat.

    Returns
    -------
    dict suitable for DominatingSet.
    """
    ThreeSat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Helper to map variable index (0‑based) to vertices
    def true_vertex(i: int) -> int:
        return 2 * i

    def false_vertex(i: int) -> int:
        return 2 * i + 1

    edges: List[List[int]] = []

    # Variable triangles: true_i, false_i, dummy_i
    for i in range(m):
        t = true_vertex(i)
        f = false_vertex(i)
        d = 2 * m + i  # dummy vertex index
        edges.append([t, f])
        edges.append([t, d])
        edges.append([f, d])

    # Clause vertices
    clause_offset = 3 * m
    for idx, clause in enumerate(clauses):
        c = clause_offset + idx
        for lit in clause:
            var = abs(lit) - 1  # zero‑based variable index
            lit_v = true_vertex(var) if lit > 0 else false_vertex(var)
            edges.append([c, lit_v])

    n = 3 * m + len(clauses)
    k = m  # one vertex per variable is enough to dominate everything

    result = {"n": n, "edges": edges, "k": k}
    DominatingSet.validate(result)
    return result

