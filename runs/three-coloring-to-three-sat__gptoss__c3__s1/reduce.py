"""Reduction from 3-Coloring to 3-SAT.

The source problem is defined by ``ThreeColoring`` in ``problems.py`` and
the target problem by ``ThreeSat``.  The instance formats are documented in
the file header and reproduced in the task description.

For each vertex ``v`` we introduce three Boolean variables ``v_R, v_G, v_B``
encoded as the integers ``3*v+1``, ``3*v+2`` and ``3*v+3`` (variables in the
target are 1‑based).  The following constraints are added:

* **Exactly one colour** – encoded by a single 3‑literal clause that at
  least one colour is chosen and three binary “at most one” constraints.
* **Edge constraints** – for every edge ``(u, v)`` and every colour ``c`` we
  add a binary clause ``¬u_c ∨ ¬v_c`` to forbid both endpoints having the
  same colour.

The target language only allows clauses with *exactly* three literals on
three distinct variables.  A binary clause ``(¬a ∨ ¬b)`` is transformed into
two 3‑literal clauses using a fresh auxiliary variable ``y``:

    (¬a ∨ ¬b ∨  y)   and   (¬a ∨ ¬b ∨ ¬y)

Both clauses must be satisfied simultaneously; this forces ``¬a ∨ ¬b`` to be
true because if ``a`` and ``b`` were both true the two clauses would become
``(y)`` and ``(¬y)`` which cannot both hold.

All auxiliary variables are distinct and numbered after the ``3*n`` colour
variables.  The reduction runs in time polynomial in the size of the input
graph.
"""

from __future__ import annotations

from typing import List, Dict

# Import the problem classes for validation and testing.
from problems import ThreeColoring, ThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described by ``ThreeColoring``.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
        that is satisfiable iff the input graph is 3‑colorable.
    """
    # Validate the source instance (will raise InvalidInstance on bad input).
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Helper to map (vertex, colour) -> variable number (1‑based).
    def var(v: int, colour: int) -> int:
        # colour: 0,1,2 for the three colours.
        return 3 * v + colour + 1

    clauses: List[List[int]] = []
    # Counter for fresh auxiliary variables.
    next_aux = 3 * n + 1

    # ---------- Vertex colour constraints ----------
    for v in range(n):
        # At least one colour.
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

        # At most one colour: pairwise constraints.
        colour_pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in colour_pairs:
            a = var(v, c1)
            b = var(v, c2)
            y = next_aux
            next_aux += 1
            # (¬a ∨ ¬b ∨  y) and (¬a ∨ ¬b ∨ ¬y)
            clauses.append([-a, -b,  y])
            clauses.append([-a, -b, -y])

    # ---------- Edge constraints ----------
    for u, v in edges:
        for colour in range(3):
            a = var(u, colour)
            b = var(v, colour)
            y = next_aux
            next_aux += 1
            clauses.append([-a, -b,  y])
            clauses.append([-a, -b, -y])

    num_vars = next_aux - 1
    return {"num_vars": num_vars, "clauses": clauses}

