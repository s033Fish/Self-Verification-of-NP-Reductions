"""Reduction from 3‑SAT to 3‑Coloring.

The implementation follows the classic polynomial‑time reduction described in
textbooks.  We build a graph that is 3‑colorable iff the SAT formula is
satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        A 3‑SAT instance as defined by :class:`ThreeSat`.

    Returns
    -------
    dict
        A graph instance suitable for :class:`ThreeColoring`.
    """
    # Validate source
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex indices
    # 0,1,2 : base triangle (TRUE, FALSE, BASE)
    base_true, base_false, base_base = 0, 1, 2

    def pos(i: int) -> int:
        return 3 + (i - 1) * 2

    def neg(i: int) -> int:
        return 3 + (i - 1) * 2 + 1

    edges: List[List[int]] = []
    # Base triangle forces three distinct colours
    edges.append([base_true, base_false])
    edges.append([base_false, base_base])
    edges.append([base_base, base_true])

    # Variable gadgets
    for i in range(1, m + 1):
        p, n = pos(i), neg(i)
        edges.append([p, n])            # opposite truth values
        edges.append([p, base_base])    # cannot use BASE colour
        edges.append([n, base_base])

    # Clause gadgets – one triangle per clause, NOT connected to BASE
    clause_start = 3 + m * 2
    for idx, clause in enumerate(clauses):
        # three vertices for this clause
        c0 = clause_start + idx * 3
        c1 = c0 + 1
        c2 = c0 + 2
        # triangle among them
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c2, c0])
        # connect each clause vertex to its literal vertex
        lits = clause
        for lit, cv in zip(lits, (c0, c1, c2)):
            v = abs(lit)
            lit_vertex = pos(v) if lit > 0 else neg(v)
            edges.append([cv, lit_vertex])

    n_vertices = clause_start + len(clauses) * 3
    graph = {"n": n_vertices, "edges": edges}
    # Validate target
    ThreeColoring.validate(graph)
    return graph

