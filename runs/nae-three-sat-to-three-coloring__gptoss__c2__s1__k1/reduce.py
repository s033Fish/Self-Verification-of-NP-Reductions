"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (``NaeThreeSat``) expects an instance of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable ``v`` should be true)
or ``-v`` (variable ``v`` should be false).  A formula is a *yes* instance iff
there exists a truth assignment where every clause contains at least one true
and at least one false literal (i.e. the three literals are *not all equal*).

The target problem (``ThreeColoring``) expects an undirected simple graph::

    {"n": n, "edges": [[u, v], ...]}

with vertices ``0 .. n-1``.  The instance is a *yes* instance iff the graph is
properly 3‑colourable.

The reduction follows the classic textbook construction:

* Introduce three *base* vertices ``0, 1, 2`` that form a triangle.  These
  enforce the three available colours.
* For each variable ``x_i`` create two vertices ``x_i^T`` and ``x_i^F``.  Both
  are adjacent to the base vertex ``2`` (so they cannot take colour ``2``) and
  are adjacent to each other, forcing one to be coloured ``0`` (interpreted as
  *true*) and the other ``1`` (interpreted as *false*).
* For each clause ``(ℓ1, ℓ2, ℓ3)`` create a triangle of three new vertices
  ``c1, c2, c3``.  Vertex ``ck`` is connected to the literal‑vertex that
  represents ``ℓk`` (positive literals use ``x_i^T`` and negative literals use
  ``x_i^F``).  The clause triangle together with the adjacency to the literal
  vertices guarantees that the clause can be coloured iff the three literals
  are *not* all assigned the same truth value – exactly the NAE condition.

The construction runs in polynomial time and produces a graph that is
3‑colourable iff the original NAE‑3‑SAT instance is satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).

    Returns
    -------
    dict
        A graph instance with keys ``"n"`` and ``"edges"`` suitable for the
        ``ThreeColoring`` problem.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    edges: List[List[int]] = []

    # ----- base triangle -------------------------------------------------
    # Vertices 0, 1, 2 form a triangle and represent the three colours.
    base_vertices = [0, 1, 2]
    edges.extend([[0, 1], [1, 2], [0, 2]])

    next_vid = 3  # next free vertex id

    # ----- variable gadgets ---------------------------------------------
    # For each variable i we create two vertices: true_i and false_i.
    var_true: Dict[int, int] = {}
    var_false: Dict[int, int] = {}
    for i in range(1, m + 1):
        true_vid = next_vid
        false_vid = next_vid + 1
        var_true[i] = true_vid
        var_false[i] = false_vid

        # Both vertices are adjacent to the base colour 2 so they cannot take
        # colour 2.  The edge between them forces them to take different colours
        # (0 and 1).
        edges.append([true_vid, 2])
        edges.append([false_vid, 2])
        edges.append([true_vid, false_vid])

        next_vid += 2

    # ----- clause gadgets ------------------------------------------------
    for clause in clauses:
        # Each clause contributes three new vertices forming a triangle.
        c1 = next_vid
        c2 = next_vid + 1
        c3 = next_vid + 2
        clause_vertices = [c1, c2, c3]

        # Triangle among the clause vertices.
        edges.append([c1, c2])
        edges.append([c2, c3])
        edges.append([c1, c3])

        # Connect each clause vertex to the appropriate literal vertex.
        for lit, cv in zip(clause, clause_vertices):
            var = abs(lit)
            if lit > 0:
                lit_vertex = var_true[var]
            else:
                lit_vertex = var_false[var]
            edges.append([cv, lit_vertex])

        next_vid += 3

    n = next_vid
    return {"n": n, "edges": edges}

