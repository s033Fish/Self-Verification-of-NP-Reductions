"""Reduction from 3-Coloring to 3-SAT.

The source problem is :class:`problems.ThreeColoring` and the target
problem is :class:`problems.ThreeSat`.  The reduction follows the classic
Cook‑Levin construction: for each vertex we create three Boolean variables
``R_v, G_v, B_v`` indicating the colour of the vertex.  The constraints are
encoded using clauses of exactly three literals (as required by the target
definition) by introducing fresh helper variables that are forced to make
the original 2‑literal constraints hold.

For a 2‑literal clause ``(a ∨ b)`` we add the pair of 3‑literal clauses

    (a ∨ b ∨ h)  and  (a ∨ b ∨ ¬h)

where ``h`` is a fresh variable.  The conjunction of the two clauses is
equivalent to ``(a ∨ b)`` because the helper variable ``h`` can take either
value, forcing the remaining literals to satisfy the original clause.

Using this trick we can express:

* **At least one colour** for each vertex – a single 3‑literal clause
  ``(R_v ∨ G_v ∨ B_v)``.
* **At most one colour** for each vertex – for each unordered pair of
  colours we add the helper pair described above on the negated literals,
  i.e. ``(¬R_v ∨ ¬G_v)`` etc.
* **Adjacent vertices differ** – for every edge ``(u, v)`` and for each
  colour ``c`` we add the helper pair on ``(¬c_u ∨ ¬c_v)``.

The reduction runs in polynomial time and produces a well‑formed 3‑SAT
instance respecting all format constraints (exactly three literals per
clause, all on distinct variables, no clause contains both a variable and
its negation).
"""

from __future__ import annotations

from typing import List, Tuple

from problems import ThreeColoring, ThreeSat


def reduce(instance: dict) -> dict:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeColoring`.

    Returns
    -------
    dict
        A dictionary adhering to the format of :class:`ThreeSat` such that
        the 3‑SAT instance is satisfiable iff the original graph is
        3‑colourable.
    """
    # Validate the source instance first.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # Variable numbering:
    #   For each vertex v (0‑based) we allocate three colour variables:
    #   var_id = v * 3 + offset, where offset is 0,1,2 for R,G,B respectively.
    #   Helper variables will be numbered after these base variables.
    base_vars = n * 3
    clauses: List[List[int]] = []

    # Helper variable generator (1‑based indexing as required by the format).
    next_helper = base_vars + 1

    def fresh_helper() -> int:
        nonlocal next_helper
        var = next_helper
        next_helper += 1
        return var

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        r = v * 3 + 1
        g = v * 3 + 2
        b = v * 3 + 3
        clauses.append([r, g, b])

    # 2. Each vertex gets at most one colour (pairwise not both true).
    for v in range(n):
        colours = [v * 3 + 1, v * 3 + 2, v * 3 + 3]
        for i in range(3):
            for j in range(i + 1, 3):
                a = -colours[i]
                b = -colours[j]
                h = fresh_helper()
                # (a ∨ b ∨ h) ∧ (a ∨ b ∨ ¬h)  enforces (a ∨ b)
                clauses.append([a, b, h])
                clauses.append([a, b, -h])

    # 3. Adjacent vertices must not share a colour.
    for (u, v) in edges:
        for colour_offset in range(3):
            a = -(u * 3 + 1 + colour_offset)
            b = -(v * 3 + 1 + colour_offset)
            h = fresh_helper()
            clauses.append([a, b, h])
            clauses.append([a, b, -h])

    num_vars = next_helper - 1
    result = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced target instance.
    ThreeSat.validate(result)
    return result

