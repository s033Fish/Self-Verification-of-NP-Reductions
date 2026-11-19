"""Reduction from 3-Coloring to 3-SAT.

The source problem is :class:`ThreeColoring` (see ``problems.py``) and the
target is :class:`ThreeSat`.  Both problems provide a ``validate`` method
that raises :class:`InvalidInstance` if the instance does not follow the
format.  Our ``reduce`` function receives a *valid* 3‑coloring instance and
produces a *valid* 3‑SAT instance such that the SAT formula is satisfiable
iff the graph is 3‑colorable.

The classic reduction uses a Boolean variable ``x_{v,c}`` meaning “vertex
``v`` receives colour ``c``”.  For each vertex we need the constraint

    (x_{v,0} ∨ x_{v,1} ∨ x_{v,2})                 (at least one colour)

and for each unordered pair of colours ``c1 < c2`` the constraint

    (¬x_{v,c1} ∨ ¬x_{v,c2})                       (at most one colour)

The target language, however, requires *exactly* three literals per clause,
all on distinct variables.  To turn a binary clause ``(a ∨ b)`` into a 3‑CNF
clause we introduce a fresh auxiliary variable ``y`` and add the pair of
clauses

    (a ∨ b ∨ y) ∧ (a ∨ b ∨ ¬y)

which is logically equivalent to ``(a ∨ b)`` because ``y`` can be chosen
arbitrarily to satisfy both clauses.

Using this trick we can express every binary constraint with two 3‑literal
clauses.  Edge constraints are similar: for an edge ``(u, v)`` and a colour
``c`` we must forbid both endpoints from taking colour ``c`` simultaneously,
which yields the binary clause ``(¬x_{u,c} ∨ ¬x_{v,c})`` and is again turned
into a pair of 3‑literal clauses with a fresh auxiliary variable.

All auxiliary variables are distinct, guaranteeing that each clause obeys
the “different variables” rule of the target definition.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, ThreeSat, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  The instance is assumed to be validated
        by :meth:`ThreeColoring.validate`.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
        satisfying the format required by :class:`ThreeSat`.
    """

    # Validate the source instance – this will raise if malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Primary variables: for each vertex v (0‑based) and colour c in {0,1,2}
    # we allocate a variable number.  Variable numbers start at 1.
    def var(v: int, c: int) -> int:
        return v * 3 + c + 1

    clauses: List[List[int]] = []
    aux_counter = 0  # counts auxiliary variables; will be added after primary ones

    # Helper to create a fresh auxiliary variable.
    def fresh_aux() -> int:
        nonlocal aux_counter
        aux_counter += 1
        # auxiliary variables follow after the primary ones
        return 3 * n + aux_counter

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. Each vertex gets at most one colour (pairwise constraints).
    for v in range(n):
        # unordered pairs of colours
        colour_pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in colour_pairs:
            a = -var(v, c1)  # ¬x_{v,c1}
            b = -var(v, c2)  # ¬x_{v,c2}
            y = fresh_aux()
            # (a ∨ b ∨ y) ∧ (a ∨ b ∨ ¬y)
            clauses.append([a, b, y])
            clauses.append([a, b, -y])

    # 3. Edge constraints: adjacent vertices cannot share the same colour.
    for u, v in edges:
        for c in range(3):
            a = -var(u, c)
            b = -var(v, c)
            y = fresh_aux()
            clauses.append([a, b, y])
            clauses.append([a, b, -y])

    num_vars = 3 * n + aux_counter
    result = {"num_vars": num_vars, "clauses": clauses}
    # Validate the target instance before returning.
    ThreeSat.validate(result)
    return result

