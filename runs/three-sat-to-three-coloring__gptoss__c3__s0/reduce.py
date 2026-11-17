"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is ``ThreeSat`` and the target is ``ThreeColoring``.  The
reduction follows the textbook construction:

* Vertices 0,1,2 form a triangle.  We interpret colour 0 as *True*, colour 1 as
  *False* and colour 2 as a neutral colour.
* For each variable x we create two vertices vt (literal x) and vf (literal ¬x).
  Both are connected to the neutral vertex 2 and to each other.  Hence vt and vf
  must receive the two colours {0,1} in opposite order – exactly one literal is
  true.
* For each clause (ℓ1 ∨ ℓ2 ∨ ℓ3) we add a triangle of three new vertices c1,c2,c3.
  Vertex ci corresponds to literal ℓi and is linked to the *opposite* literal
  vertex of the variable: a positive literal x connects to vf, a negative literal
  ¬x connects to vt.  The clause triangle can be properly coloured iff at least
  one of its vertices can take the neutral colour 2, which happens precisely when
  the corresponding literal is true.  Thus the clause gadget is colourable iff the
  clause is satisfied.

The resulting graph is 3‑colourable iff the original formula is satisfiable.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SOURCE, TARGET


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` – format of
        :class:`ThreeSat`.

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` – a graph suitable for
        :class:`ThreeColoring`.
    """

    # Validate the source instance.
    SOURCE.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertices 0,1,2 are the colour vertices (True, False, Base).
    edges: List[List[int]] = []
    edges.extend([[0, 1], [1, 2], [0, 2]])  # triangle among colour vertices

    var_true: List[int] = []   # vertex representing literal x
    var_false: List[int] = []  # vertex representing literal ¬x

    next_idx = 3
    for _ in range(m):
        vt = next_idx      # literal x
        vf = next_idx + 1  # literal ¬x
        var_true.append(vt)
        var_false.append(vf)
        # Both literal vertices connect to the neutral colour vertex (2) so they
        # cannot take colour 2.  The edge between them forces them to take colours
        # 0 and 1 in opposite order.
        edges.append([vt, 2])
        edges.append([vf, 2])
        edges.append([vt, vf])
        next_idx += 2

    # Clause gadgets.
    for clause in clauses:
        c0, c1, c2 = next_idx, next_idx + 1, next_idx + 2
        next_idx += 3
        # Triangle among the clause vertices.
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c2, c0])
        for lit, cv in zip(clause, (c0, c1, c2)):
            var = abs(lit) - 1
            if lit > 0:
                # Positive literal x → connect to ¬x vertex (vf)
                opposite = var_false[var]
            else:
                # Negative literal ¬x → connect to x vertex (vt)
                opposite = var_true[var]
            edges.append([cv, opposite])

    graph_instance: Dict[str, Any] = {"n": next_idx, "edges": edges}
    TARGET.validate(graph_instance)
    return graph_instance

