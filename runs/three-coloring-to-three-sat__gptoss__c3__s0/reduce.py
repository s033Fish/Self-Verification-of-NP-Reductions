"""Reduction from 3-Coloring to 3-SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability).
The target problem is :class:`ThreeSat` (exactly‑3‑CNF satisfiability).

We encode each vertex with three Boolean variables representing the three
possible colours.  The constraints are:

* each vertex receives **at least one** colour – a single 3‑literal clause;
* each vertex receives **at most one** colour – for every unordered pair of
  colours we need a clause (¬x ∨ ¬y).  Because the target format requires
  exactly three literals on three distinct variables, we replace each 2‑literal
  clause (ℓ1 ∨ ℓ2) by the pair of 3‑literal clauses
  (ℓ1 ∨ ℓ2 ∨ a) ∧ (ℓ1 ∨ ℓ2 ∨ ¬a) using a fresh auxiliary variable *a*.
* adjacent vertices must not share a colour – again a 2‑literal clause for each
  colour, encoded with a fresh auxiliary variable as above.

The construction introduces O(|V|+|E|) auxiliary variables, so the total number
of variables is polynomial.  The reduction runs in polynomial time and the
resulting 3‑SAT instance is satisfiable iff the original graph is 3‑colorable.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, ThreeSat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as specified by
        :class:`ThreeColoring`.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable iff the original graph is 3‑colorable.
    """
    # Validate source instance.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping from vertex i and colour c (0,1,2) to SAT variable number.
    def var(i: int, colour: int) -> int:
        return 3 * i + colour + 1  # variables are 1‑based

    # Auxiliary variables start after the colour variables.
    next_aux = 3 * n  # highest used will be next_aux after loop
    clauses: List[List[int]] = []

    # Vertex constraints.
    for i in range(n):
        r, g, b = var(i, 0), var(i, 1), var(i, 2)
        # At least one colour.
        clauses.append([r, g, b])
        # At most one colour: for each pair (¬x ∨ ¬y) introduce aux variable.
        for x, y in [(r, g), (r, b), (g, b)]:
            aux = next_aux + 1
            next_aux += 1
            # (¬x ∨ ¬y ∨  a) ∧ (¬x ∨ ¬y ∨ ¬a)
            clauses.append([-x, -y, aux])
            clauses.append([-x, -y, -aux])

    # Edge constraints: adjacent vertices cannot share a colour.
    for u, v in edges:
        for colour in range(3):
            cu = var(u, colour)
            cv = var(v, colour)
            aux = next_aux + 1
            next_aux += 1
            clauses.append([-cu, -cv, aux])
            clauses.append([-cu, -cv, -aux])

    m = next_aux  # total number of variables used
    reduced_instance: Dict[str, Any] = {"num_vars": m, "clauses": clauses}
    # Validate target instance (helps catch mistakes).
    ThreeSat.validate(reduced_instance)
    return reduced_instance

