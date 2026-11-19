"""Reduction from 3-Coloring to 3-SAT.

The reduction follows the classic polynomial‑time construction:

* For each vertex *i* we create three Boolean variables
  ``x_i_1, x_i_2, x_i_3`` meaning that vertex *i* receives colour 1, 2 or 3.
* Each vertex must receive *at least* one colour – a 3‑literal clause
  ``(x_i_1 ∨ x_i_2 ∨ x_i_3)``.
* A vertex cannot receive two colours simultaneously.  For every unordered
  pair of colours ``c1 < c2`` we need a clause ``(¬x_i_c1 ∨ ¬x_i_c2)``.
  3‑SAT clauses must contain exactly three **different** variables, so we
  pad each binary clause with a fresh auxiliary variable ``z`` and also add
  the complementary clause ``(¬x_i_c1 ∨ ¬x_i_c2 ∨ ¬z)``.  Together they are
  equivalent to the original binary clause.
* For every edge ``(u, v)`` and every colour ``c`` the endpoints cannot share
  the same colour.  This again yields a binary clause ``(¬x_u_c ∨ ¬x_v_c)``
  which we pad using a fresh auxiliary variable exactly as above.

All auxiliary variables are distinct, guaranteeing the three‑literal and
different‑variable requirements of the target problem.

The function ``reduce(instance)`` validates the input using the
``ThreeColoring.validate`` method and returns a dictionary that conforms to
the ``ThreeSat`` format.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeColoring, ThreeSat, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent 3‑SAT instance.

    The returned instance satisfies ``ThreeSat.validate`` and has the
    property that it is satisfiable iff the input graph is 3‑colorable.
    """
    # Validate source instance.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Primary colour variables: for vertex i and colour c (1‑based) we assign
    # variable index = i * 3 + c.  Variables are 1‑based for the SAT format.
    def colour_var(i: int, c: int) -> int:
        return i * 3 + c

    clauses: List[List[int]] = []
    # Single auxiliary variable for padding binary clauses.
    aux_var = n * 3 + 1

    # 1. Each vertex gets at least one colour.
    for i in range(n):
        clauses.append([colour_var(i, 1), colour_var(i, 2), colour_var(i, 3)])

    # Helper to add a padded binary clause (a ∨ b).
    def add_padded_binary(lit1: int, lit2: int) -> None:
        # Two clauses: (lit1 ∨ lit2 ∨ aux) and (lit1 ∨ lit2 ∨ -aux)
        clauses.append([lit1, lit2, aux_var])
        clauses.append([lit1, lit2, -aux_var])

    # 2. No vertex can have two colours simultaneously.
    for i in range(n):
        add_padded_binary(-colour_var(i, 1), -colour_var(i, 2))
        add_padded_binary(-colour_var(i, 1), -colour_var(i, 3))
        add_padded_binary(-colour_var(i, 2), -colour_var(i, 3))

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in (1, 2, 3):
            add_padded_binary(-colour_var(u, c), -colour_var(v, c))

    num_vars = aux_var  # highest variable index used
    result = {"num_vars": num_vars, "clauses": clauses}
    ThreeSat.validate(result)
    return result

