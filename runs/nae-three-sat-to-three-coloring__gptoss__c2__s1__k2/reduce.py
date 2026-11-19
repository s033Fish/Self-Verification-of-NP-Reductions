"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (``NaeThreeSat``) is described in ``problems.py`` as a
 dictionary with the keys ``"num_vars"`` and ``"clauses"``.  A clause is a list
 of three literals where a literal is a signed integer: ``+v`` represents the
 positive literal of variable ``v`` and ``-v`` the negative literal.

The target problem (``ThreeColoring``) expects a dictionary with the keys
 ``"n"`` (number of vertices) and ``"edges"`` (list of undirected edges ``[u, v]``).

We implement the classic polynomial‑time reduction that uses a base triangle
 to fix the three colours and gadgets for variables and clauses.  The reduction
 has the following properties:

* The three vertices ``0, 1, 2`` form a triangle.  Their colours can be viewed
  as ``TRUE``, ``FALSE`` and ``THIRD`` respectively.
* For each variable ``x`` we create two vertices ``pos`` and ``neg`` (one for
  the positive literal, one for the negative literal).  Both are adjacent to
  the ``THIRD`` vertex, forcing them to take only the ``TRUE`` or ``FALSE``
  colour.  An edge between ``pos`` and ``neg`` forces them to receive opposite
  colours, i.e. one is ``TRUE`` and the other ``FALSE``.
* For each clause ``(l1, l2, l3)`` we create a triangle of three new vertices
  ``c1, c2, c3``.  Each ``ci`` is adjacent to the vertex representing the
  corresponding literal ``li``.  The triangle forces the three ``ci`` to have
  three distinct colours.  If all three literals received the same colour
  (all true or all false) then each ``ci`` would be prohibited from that
  colour, leaving only two colours for three vertices – impossible.  Hence the
  clause gadget enforces the *not‑all‑equal* condition.

The construction runs in time linear in the size of the NAE‑3‑SAT instance
 and produces a graph that is 3‑colourable iff the original formula is
 NAE‑satisfiable.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of literals).  Literals are signed integers where
        ``+v`` denotes the positive literal of variable ``v`` and ``-v`` the
        negative literal.

    Returns
    -------
    dict
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs) representing the constructed graph.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    edges: List[Tuple[int, int]] = []

    # ---------------------------------------------------------------------
    # 1. Base triangle (vertices 0, 1, 2).  They will play the role of the
    #    three colours.  No further edges are needed for them beyond the
    #    triangle itself.
    # ---------------------------------------------------------------------
    base_true = 0
    base_false = 1
    base_third = 2
    edges.extend([(base_true, base_false), (base_false, base_third), (base_true, base_third)])

    # ---------------------------------------------------------------------
    # 2. Variable gadgets.
    #    For each variable i (1‑based) we create two vertices:
    #        pos_i  – vertex for the positive literal +i
    #        neg_i  – vertex for the negative literal -i
    #    Both are connected to the ``base_third`` vertex to forbid using that
    #    colour, and an edge between them forces opposite colours.
    # ---------------------------------------------------------------------
    pos_vertices: List[int] = [0] * (m + 1)  # 1‑based indexing; entry 0 unused
    neg_vertices: List[int] = [0] * (m + 1)

    next_vertex = 3  # after the base triangle
    for var in range(1, m + 1):
        pos = next_vertex
        neg = next_vertex + 1
        pos_vertices[var] = pos
        neg_vertices[var] = neg
        next_vertex += 2

        # Connect to the third colour vertex
        edges.append((pos, base_third))
        edges.append((neg, base_third))
        # Force opposite colours
        edges.append((pos, neg))

    # ---------------------------------------------------------------------
    # 3. Clause gadgets.
    #    For each clause we add three new vertices forming a triangle.  Each
    #    vertex of the clause triangle is connected to the vertex representing
    #    the corresponding literal.
    # ---------------------------------------------------------------------
    for clause in clauses:
        if len(clause) != 3:
            # The problem statement guarantees exactly three literals, but we
            # guard against malformed input for robustness.
            raise ValueError("Each clause must contain exactly three literals")

        # Create the three clause vertices
        c1 = next_vertex
        c2 = next_vertex + 1
        c3 = next_vertex + 2
        next_vertex += 3

        # Triangle among clause vertices
        edges.extend([(c1, c2), (c2, c3), (c1, c3)])

        # Connect each clause vertex to its literal vertex
        for lit, clause_vertex in zip(clause, (c1, c2, c3)):
            var = abs(lit)
            if var == 0 or var > m:
                raise ValueError("Literal refers to non‑existent variable")
            if lit > 0:
                literal_vertex = pos_vertices[var]
            else:
                literal_vertex = neg_vertices[var]
            edges.append((clause_vertex, literal_vertex))

    # ---------------------------------------------------------------------
    # 4. Assemble the final instance.
    # ---------------------------------------------------------------------
    n = next_vertex  # total number of vertices created
    # Convert edge tuples to the required list format and ensure each edge
    # appears only once (the construction never creates duplicates).
    edge_list: List[List[int]] = [[u, v] for u, v in edges]

    return {"n": n, "edges": edge_list}

