"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is ``NaeThreeSat`` (not‑all‑equal 3‑SAT) and the target
problem is ``ThreeColoring``. Both problems are defined in ``problems.py``
with the instance formats reproduced in the task description.

The construction follows the classic polynomial‑time reduction (see
Garey & Johnson). We create a distinguished triangle of vertices that will be
forced to receive the three different colours. These three colours are
interpreted as:

* vertex ``T`` – colour representing logical **TRUE**
* vertex ``F`` – colour representing logical **FALSE**
* vertex ``R`` – a *reference* colour used only as a helper.

For each Boolean variable ``v`` we introduce two vertices ``v_T`` and
``v_F``. The edges are arranged so that in any proper 3‑colouring exactly one
of them receives the colour of ``T`` and the other receives the colour of
``F`` (the third colour ``R`` may be used for at most one of the two). The
choice of which receives ``T`` encodes the truth value of the variable.

Clause gadgets enforce the NAE condition. For a clause ``(ℓ1, ℓ2, ℓ3)`` we
create three fresh vertices ``c1, c2, c3`` forming a triangle. Each ``ci`` is
adjacent both to the reference vertex ``R`` and to the literal vertex that
represents the corresponding literal (``v_T`` for a positive literal and
``v_F`` for a negative literal). If all three literals were coloured the
same (all TRUE or all FALSE) then each ``ci`` would be forbidden from using
that colour as well as the colour of ``R``; consequently all three ``ci``
would be forced to the remaining colour, which is impossible because they
form a triangle. Hence a proper 3‑colouring exists iff every clause has at
least one true and one false literal – exactly the NAE‑3‑SAT condition.

The reduction runs in polynomial time: the number of vertices and edges is
linear in the number of variables and clauses.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (``m``) and ``"clauses"`` – a
        list of clauses, each clause being a list of three literals. A
        literal is an integer ``+v`` for a positive occurrence of variable
        ``v`` and ``-v`` for a negated occurrence.

    Returns
    -------
    dict
        A dictionary representing a graph: ``{"n": n, "edges": [[u, v], …]}``
        where vertices are numbered ``0 … n‑1``.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[Tuple[int, int]] = []

    # Helper to add an undirected edge without creating duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # ------------------------------------------------------------------
    # 1. Create the special triangle (T, F, R).
    # ------------------------------------------------------------------
    T, F, R = 0, 1, 2
    add_edge(T, F)
    add_edge(F, R)
    add_edge(R, T)

    next_vertex = 3  # next free vertex id

    # Maps from variable index to the vertices representing the literal
    # vertices in the graph.
    var_true: Dict[int, int] = {}
    var_false: Dict[int, int] = {}

    # ------------------------------------------------------------------
    # 2. Variable gadgets.
    # ------------------------------------------------------------------
    for v in range(1, m + 1):
        vt = next_vertex
        vf = next_vertex + 1
        next_vertex += 2
        var_true[v] = vt
        var_false[v] = vf

        # Connect vt to the TRUE vertex, vf to the FALSE vertex.
        add_edge(vt, T)
        add_edge(vf, F)
        # Edge between vt and vf forces opposite colours.
        add_edge(vt, vf)
        # Optional edges to the reference vertex help keep the gadget
        # well‑behaved but are not strictly necessary. Adding them does not
        # affect correctness.
        add_edge(vt, R)
        add_edge(vf, R)

    # ------------------------------------------------------------------
    # 3. Clause gadgets.
    # ------------------------------------------------------------------
    for clause in clauses:
        # clause is a list of three literals, each literal is an int with
        # sign indicating polarity.
        lit_vertices: List[int] = []
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                lit_vertices.append(var_true[var])
            else:
                lit_vertices.append(var_false[var])

        # Create three clause vertices forming a triangle.
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3

        # Triangle among clause vertices.
        add_edge(c_vertices[0], c_vertices[1])
        add_edge(c_vertices[1], c_vertices[2])
        add_edge(c_vertices[2], c_vertices[0])

        # Connect each clause vertex to its corresponding literal vertex and
        # to the reference vertex R.
        for ci, li in zip(c_vertices, lit_vertices):
            add_edge(ci, li)
            add_edge(ci, R)

    # ------------------------------------------------------------------
    # 4. Assemble final graph description.
    # ------------------------------------------------------------------
    # Convert edge tuples to the required list format, ensuring each edge
    # appears exactly once.
    edge_list = [list(e) for e in edges]
    n = next_vertex
    return {"n": n, "edges": edge_list}

