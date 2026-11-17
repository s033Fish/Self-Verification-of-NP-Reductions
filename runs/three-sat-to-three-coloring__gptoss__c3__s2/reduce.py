"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is :class:`ThreeSat` (see ``problems.py``) and the
target is :class:`ThreeColoring`. The reduction follows the classic
polynomial‑time construction used in textbooks:

* Create three special vertices forming a triangle – they will be forced to
  receive three distinct colours.  We name them ``TRUE``, ``FALSE`` and
  ``BASE``.
* For each Boolean variable ``x_i`` we create two vertices ``x_i`` and
  ``¬x_i``.  Both are adjacent to ``BASE`` (so they cannot take the base
  colour) and they are adjacent to each other, forcing them to receive the
  remaining two colours – one will be coloured ``TRUE`` and the other
  ``FALSE``.  Which of the pair receives ``TRUE`` encodes the truth value
  of the variable.
* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a triangle of three new
  vertices.  Vertex ``c_j`` of the clause‑triangle is connected to the
  literal vertex that represents ``ℓj`` (positive literal → the ``x``
  vertex, negative literal → the ``¬x`` vertex).  Additionally each clause
  vertex is connected to the ``FALSE`` vertex.  This forces the clause‑triangle
  to be colourable only if at least one of its neighbours (the literal
  vertices) is coloured ``TRUE``; otherwise the three vertices would have to
  use only the two colours ``TRUE`` and ``BASE`` which is impossible for a
  triangle.

The resulting graph is 3‑colourable iff the original formula is
satisfiable.  The construction uses a linear number of vertices and edges
with respect to the size of the SAT instance, thus runs in polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``ThreeSat`` specification.

    Returns
    -------
    dict
        A graph instance suitable for ``ThreeColoring``.
    """
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Special colour vertices
    TRUE = 0
    FALSE = 1
    BASE = 2
    next_id = 3

    # Triangle among TRUE, FALSE, BASE
    edges.extend([[TRUE, FALSE], [FALSE, BASE], [BASE, TRUE]])

    # Variable gadgets
    pos_of: Dict[int, int] = {}
    neg_of: Dict[int, int] = {}
    for v in range(1, num_vars + 1):
        pos = next_id
        neg = next_id + 1
        next_id += 2
        pos_of[v] = pos
        neg_of[v] = neg
        # variable edge and connections to BASE (cannot use BASE colour)
        edges.append([pos, neg])
        edges.append([pos, BASE])
        edges.append([neg, BASE])

    # Clause gadgets
    for clause in clauses:
        # three new vertices for this clause
        c0, c1, c2 = next_id, next_id + 1, next_id + 2
        next_id += 3
        # triangle among them
        edges.extend([[c0, c1], [c1, c2], [c2, c0]])
        # connect each clause vertex to FALSE to prohibit using FALSE colour only
        edges.extend([[c0, FALSE], [c1, FALSE], [c2, FALSE]])
        # connect to the appropriate literal vertices
        for lit, c_vert in zip(clause, (c0, c1, c2)):
            var = abs(lit)
            lit_vertex = pos_of[var] if lit > 0 else neg_of[var]
            edges.append([c_vert, lit_vertex])

    graph = {"n": next_id, "edges": edges}
    ThreeColoring.validate(graph)
    return graph

