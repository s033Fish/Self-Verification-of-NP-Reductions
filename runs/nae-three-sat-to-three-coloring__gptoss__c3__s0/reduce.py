"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is :class:`problems.NaeThreeSat` and the target is
`problems.ThreeColoring`.  The reduction follows the classic polynomial‑time
construction that uses three colours – we call them **T**, **F** and **B** –
where the special vertex ``B`` (the base vertex) is forced to receive colour
``B``.

For each variable ``x`` we create a triangle consisting of the base vertex
and two vertices representing the literal ``x`` (true) and ``¬x`` (false).
This forces exactly one of the two literal vertices to be coloured ``T``
and the other ``F``.

For every clause ``(ℓ₁, ℓ₂, ℓ₃)`` we add a fresh triangle (the *clause
triangle*) and connect each literal vertex to a *different* vertex of this
triangle.  If all three literals receive the same colour (all true or all
false) then each vertex of the clause triangle is forbidden that colour,
leaving only two colours for three mutually adjacent vertices – an
impossibility.  When the literals are not all equal, a proper 3‑colouring
exists by assigning the three clause vertices the three distinct colours.

The construction runs in linear time in the size of the formula and
produces a simple undirected graph suitable for ``ThreeColoring``.
"""

from __future__ import annotations

from typing import List, Tuple

import problems  # The provided module containing problem definitions.


def reduce(instance: problems.Instance) -> problems.Instance:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined by
        :class:`problems.NaeThreeSat`.

    Returns
    -------
    dict
        A graph instance ``{"n": n, "edges": [[u, v], ...]}`` suitable for
        :class:`problems.ThreeColoring`.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong, matching the expectations of the surrounding harness.
    problems.NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # ------------------------------------------------------------------
    # Vertex allocation
    # ------------------------------------------------------------------
    # Vertex 0 is the special base vertex (colour B).
    base = 0
    next_vid = 1

    # For each variable i we store the vertex id of the literal i (true) and
    # the literal ¬i (false).
    var_true: List[int] = [0] * (m + 1)   # index 0 unused
    var_false: List[int] = [0] * (m + 1)
    for i in range(1, m + 1):
        var_true[i] = next_vid
        next_vid += 1
        var_false[i] = next_vid
        next_vid += 1

    # Clause triangles – three fresh vertices per clause.
    clause_vertices: List[Tuple[int, int, int]] = []
    for _ in clauses:
        c1 = next_vid
        c2 = next_vid + 1
        c3 = next_vid + 2
        next_vid += 3
        clause_vertices.append((c1, c2, c3))

    n = next_vid  # total number of vertices

    # ------------------------------------------------------------------
    # Edge construction
    # ------------------------------------------------------------------
    edges: List[List[int]] = []

    # Variable gadgets: each (base, true, false) forms a triangle.
    for i in range(1, m + 1):
        vt = var_true[i]
        vf = var_false[i]
        edges.append([base, vt])
        edges.append([base, vf])
        edges.append([vt, vf])

    # Clause gadgets – the three vertices of each clause form a triangle.
    for (c1, c2, c3) in clause_vertices:
        edges.append([c1, c2])
        edges.append([c2, c3])
        edges.append([c3, c1])

    # Connect each literal to the corresponding vertex of its clause triangle.
    for clause_idx, clause in enumerate(clauses):
        c1, c2, c3 = clause_vertices[clauses.index(clause)] if False else clause_vertices[clause_idx]
        clause_vs = [c1, c2, c3]
        for pos, lit in enumerate(clause):
            var = abs(lit)
            lit_vertex = var_true[var] if lit > 0 else var_false[var]
            edges.append([lit_vertex, clause_vs[pos]])

    # The target problem expects exactly the keys "n" and "edges".
    return {"n": n, "edges": edges}

