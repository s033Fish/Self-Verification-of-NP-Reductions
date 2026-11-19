"""Reduction from NAE-3-SAT to 3-Coloring.

The reduction follows the classic construction used in many textbooks:

* We use three distinguished colours which we model as three vertices that
  form a triangle.  We name them ``TRUE`` (0), ``FALSE`` (1) and ``DUMMY`` (2).
* For each variable ``x`` we create two vertices ``x`` and ``¬x``.  Both are
  connected to the ``DUMMY`` vertex, forcing them to be coloured either
  ``TRUE`` or ``FALSE``.  An edge between ``x`` and ``¬x`` guarantees that the
  two vertices receive opposite colours, i.e. one is ``TRUE`` and the other
  ``FALSE``.
* For each clause ``(ℓ₁, ℓ₂, ℓ₃)`` we add a triangle of three fresh vertices
  ``c₁, c₂, c₃``.  Vertex ``c_k`` is connected to the vertex representing the
  literal ``ℓ_k`` (the positive or negative variable vertex).  The clause
  triangle forces the three ``c``‑vertices to receive three distinct colours.
  Because each ``c_k`` is adjacent to its literal vertex, ``c_k`` cannot use
  the colour of that literal.  Consequently the three literals cannot all be
  coloured the same – otherwise the clause triangle would have only two
  colours available, which is impossible.  Conversely, if the clause is not
  all‑equal, a proper 3‑colouring exists.

The function ``reduce`` builds this graph and returns it in the format
required by :class:`ThreeColoring` (a dict with keys ``"n"`` and ``"edges"``).
"""

from __future__ import annotations

from typing import Dict, List

from problems import NaeThreeSat, ThreeColoring

def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``NaeThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``ThreeColoring`` format such that the
        original instance is satisfiable under the NAE condition iff the
        returned graph is 3‑colourable.
    """
    # Validate the source instance first – this raises ``InvalidInstance``
    # if the input is malformed.
    NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []
    # Vertex numbering strategy:
    # 0,1,2  – the base triangle (TRUE, FALSE, DUMMY)
    # 3..3+2*m-1 – variable vertices (positive then negative for each var)
    # remaining – clause‑gadget vertices, three per clause.
    TRUE, FALSE, DUMMY = 0, 1, 2
    # base triangle
    edges += [[TRUE, FALSE], [FALSE, DUMMY], [TRUE, DUMMY]]

    # Helper lists to map variable index to its positive/negative vertex.
    pos_vertex: List[int] = []  # index var-1
    neg_vertex: List[int] = []
    next_id = 3
    for var in range(1, m + 1):
        pos = next_id
        neg = next_id + 1
        next_id += 2
        pos_vertex.append(pos)
        neg_vertex.append(neg)
        # Connect each to DUMMY so they cannot take colour DUMMY.
        edges.append([pos, DUMMY])
        edges.append([neg, DUMMY])
        # Force opposite colours.
        edges.append([pos, neg])

    # Clause gadgets
    for clause in clauses:
        # Create three new vertices for the clause triangle.
        c_vertices = [next_id, next_id + 1, next_id + 2]
        next_id += 3
        # Triangle edges among them.
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])
        # Connect each clause vertex to the corresponding literal vertex.
        for lit, c_v in zip(clause, c_vertices):
            var = abs(lit)
            if lit > 0:
                lit_vertex = pos_vertex[var - 1]
            else:
                lit_vertex = neg_vertex[var - 1]
            edges.append([c_v, lit_vertex])

    result: Dict = {"n": next_id, "edges": edges}
    # Validate the produced graph to ensure correctness of construction.
    ThreeColoring.validate(result)
    return result

