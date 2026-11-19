"""Reduction from 3‑SAT to 3‑Coloring.

The reduction follows the classic construction:

* A base triangle with vertices TRUE, FALSE and BASE.  In any proper 3‑colouring
  they receive three distinct colours.
* For each variable x we create two vertices ``v_true`` and ``v_false``.
  - ``v_true`` is adjacent to the FALSE vertex and to BASE.
  - ``v_false`` is adjacent to the TRUE vertex and to BASE.
  - ``v_true`` and ``v_false`` are adjacent to each other.
  Because ``v_true`` cannot use the colours of FALSE or BASE it must take the
  colour of TRUE; similarly ``v_false`` must take the colour of FALSE.  Thus the
  colour of ``v_true`` encodes the assignment *x = true* and the colour of
  ``v_false`` encodes *x = false*.
* For each clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we create a triangle of three new vertices.
  The i‑th vertex of the clause triangle is connected to the variable vertex
  that would be coloured **TRUE** when literal ℓᵢ is satisfied:
    - a positive literal +v connects to ``v_true`` of variable v;
    - a negative literal –v connects to ``v_false`` of variable v.
  If all three literals of a clause are false, each clause vertex is forced to
  avoid the colour TRUE, leaving only two colours for a three‑vertex triangle –
  impossible.  Hence a proper 3‑colouring exists iff the original formula is
  satisfiable.

The construction runs in polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` describing a
        3‑SAT formula.

    Returns
    -------
    dict
        A graph instance suitable for :class:`ThreeColoring`.
    """

    ThreeSat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # 1. Base triangle.
    TRUE, FALSE, BASE = 0, 1, 2
    edges.extend([[TRUE, FALSE], [FALSE, BASE], [BASE, TRUE]])

    # 2. Variable gadgets.
    var_true: List[int] = []   # vertex representing the literal x (true)
    var_false: List[int] = []  # vertex representing the literal ¬x (false)
    nxt = 3
    for _ in range(m):
        v_true = nxt      # adjacent to FALSE and BASE
        v_false = nxt + 1 # adjacent to TRUE and BASE
        nxt += 2
        var_true.append(v_true)
        var_false.append(v_false)
        # edge between the two literal vertices (forces opposite colours)
        edges.append([v_true, v_false])
        # connections to base triangle
        edges.append([v_true, FALSE])
        edges.append([v_true, BASE])
        edges.append([v_false, TRUE])
        edges.append([v_false, BASE])

    # 3. Clause gadgets.
    for clause in clauses:
        # three vertices forming a triangle for this clause
        c0, c1, c2 = nxt, nxt + 1, nxt + 2
        nxt += 3
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c2, c0])
        for lit, cv in zip(clause, (c0, c1, c2)):
            var = abs(lit) - 1
            if lit > 0:
                # positive literal connects to the vertex that is TRUE when x is true
                lit_vertex = var_true[var]
            else:
                # negative literal connects to the vertex that is TRUE when ¬x is true
                lit_vertex = var_false[var]
            edges.append([cv, lit_vertex])

    graph_instance: Dict = {"n": nxt, "edges": edges}
    ThreeColoring.validate(graph_instance)
    return graph_instance

