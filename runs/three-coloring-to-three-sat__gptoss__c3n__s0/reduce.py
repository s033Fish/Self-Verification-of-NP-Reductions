"""Reduction from 3-Coloring to 3-SAT.

The source problem is defined in :class:`problems.ThreeColoring` and the
target in :class:`problems.ThreeSat`.  Both classes only provide a
``validate`` method – there are no solvers.  This file implements a
polynomial‑time many‑one reduction that maps a graph instance to a 3‑CNF
formula such that the formula is satisfiable iff the graph is 3‑colorable.

The construction follows the classic textbook reduction:

* For each vertex ``v`` we introduce three Boolean variables
  ``R_v, G_v, B_v`` meaning that ``v`` receives the respective colour.
* A vertex must receive *at least* one colour – encoded by the clause
  ``(R_v ∨ G_v ∨ B_v)`` which already has three literals.
* A vertex must receive *at most* one colour.  For each unordered pair
  of colours we need a clause ``(¬R_v ∨ ¬G_v)`` etc.  These are 2‑literal
  clauses, but 3‑SAT requires exactly three literals on three distinct
  variables.  We pad each 2‑literal clause using a fresh variable ``y``
  by adding the two clauses ``(¬R_v ∨ ¬G_v ∨ y)`` and
  ``(¬R_v ∨ ¬G_v ∨ ¬y)``.  This technique forces at least one of the two
  original literals to be true regardless of the value of ``y``.
* For each edge ``(u, v)`` and each colour ``c`` we forbid both endpoints
  from sharing ``c`` – again a 2‑literal clause ``(¬c_u ∨ ¬c_v)`` padded
  in the same way.

All padding variables are fresh, guaranteeing that every clause contains
three *different* variables, as required by the target specification.

The reduction runs in time O(|V| + |E|) and produces a formula with
``m = 6·|V| + 3·|E|`` variables and a linear number of clauses.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, ThreeSat, InvalidInstance


def _var_id(vertex: int, colour: int) -> int:
    """Return the base variable identifier for a vertex/colour pair.

    Vertices are numbered 0..n‑1, colours are 0,1,2 (representing R,G,B).
    The identifiers start at 1, as required by the 3‑SAT format.
    """
    return vertex * 3 + colour + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dict adhering to the format described in ``ThreeColoring``.

    Returns
    -------
    dict
        A 3‑SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance – this will raise ``InvalidInstance``
    # if the input is malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []
    # Keep track of the next fresh variable identifier for padding.
    next_var: int = 3 * n + 1  # after the base colour variables

    # ----- Vertex constraints -----
    for v in range(n):
        # At least one colour: (R_v ∨ G_v ∨ B_v)
        r = _var_id(v, 0)
        g = _var_id(v, 1)
        b = _var_id(v, 2)
        clauses.append([r, g, b])

        # At most one colour – pad each 2‑literal clause.
        pairs = [(r, g), (r, b), (g, b)]
        for a, b_ in pairs:
            y = next_var
            next_var += 1
            # (¬a ∨ ¬b ∨  y) and (¬a ∨ ¬b ∨ ¬y)
            clauses.append([-a, -b_, y])
            clauses.append([-a, -b_, -y])

    # ----- Edge constraints -----
    for u, v in edges:
        for colour in range(3):
            a = _var_id(u, colour)
            b = _var_id(v, colour)
            y = next_var
            next_var += 1
            # (¬a ∨ ¬b ∨  y) and (¬a ∨ ¬b ∨ ¬y)
            clauses.append([-a, -b, y])
            clauses.append([-a, -b, -y])

    num_vars = next_var - 1
    # Validate the produced target instance before returning.
    target_instance = {"num_vars": num_vars, "clauses": clauses}
    ThreeSat.validate(target_instance)
    return target_instance

