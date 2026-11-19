"""Reduction from 3-Coloring to 3-SAT.

The source problem is defined by :class:`problems.ThreeColoring` and the
target by :class:`problems.ThreeSat`.  Both classes provide ``validate`` and
``is_yes`` class methods that we can use for testing.

The reduction creates a Boolean variable for each colour of each vertex and
adds clauses that enforce:

1. *Exactly* one colour per vertex (at least one – a 3‑literal clause, and
   at most one – encoded as a pair of 3‑literal clauses using an auxiliary
   variable).
2. Adjacent vertices must not share a colour (again a binary constraint
   encoded with an auxiliary variable).

All clauses contain three *different* variables, satisfying the strict 3‑SAT
format required by the benchmark.
"""

from __future__ import annotations

from typing import List

from problems import ThreeColoring, ThreeSat


def _next_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a single‑element list used to emulate a mutable integer
    across function calls (avoiding the ``nonlocal`` keyword for Python 3.7
    compatibility).  The first call returns the value stored in the list and
    then increments it.
    """

    v = counter[0]
    counter[0] += 1
    return v


def reduce(instance: dict) -> dict:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described in the docstring of
        :class:`problems.ThreeColoring` – it must contain the keys ``"n"`` and
        ``"edges"``.

    Returns
    -------
    dict
        A 3‑SAT instance in the format required by :class:`problems.ThreeSat`
        (keys ``"num_vars"`` and ``"clauses"``).
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed, matching the behaviour expected of a reduction.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Primary colour variables: three per vertex.
    # Variable numbering starts at 1, as required by the SAT format.
    # For vertex v (0‑based) the colours are:
    #   red   = v*3 + 1
    #   green = v*3 + 2
    #   blue  = v*3 + 3
    base_vars = 3 * n
    var_counter = [base_vars + 1]  # next fresh auxiliary variable index

    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour (a single 3‑literal clause).
    for v in range(n):
        r = v * 3 + 1
        g = v * 3 + 2
        b = v * 3 + 3
        clauses.append([r, g, b])

        # 2. At most one colour – encode ¬(c_i ∧ c_j) using an auxiliary variable a:
        #    (¬c_i ∨ ¬c_j ∨ a) ∧ (¬c_i ∨ ¬c_j ∨ ¬a)
        for (c1, c2) in [(r, g), (r, b), (g, b)]:
            a = _next_var(var_counter)
            clauses.append([-c1, -c2, a])
            clauses.append([-c1, -c2, -a])

    # 3. Edge constraints – for each edge and each colour, the two endpoints
    #    cannot both have that colour.
    for u, v in edges:
        for colour_offset in range(3):
            cu = u * 3 + 1 + colour_offset
            cv = v * 3 + 1 + colour_offset
            a = _next_var(var_counter)
            clauses.append([-cu, -cv, a])
            clauses.append([-cu, -cv, -a])

    num_vars = var_counter[0] - 1  # the last used variable index
    sat_instance = {"num_vars": num_vars, "clauses": clauses}

    # Validate the produced target instance to catch any accidental format
    # errors early.
    ThreeSat.validate(sat_instance)
    return sat_instance

