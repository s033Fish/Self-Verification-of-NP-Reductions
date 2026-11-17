"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined in :class:`problems.ThreeSat` and the target
in :class:`problems.ThreeColoring`.  Both classes only provide a ``validate``
method – there are no solvers.  This module implements ``reduce`` which
converts a 3‑SAT instance to a graph such that the graph is 3‑colorable iff
the formula is satisfiable.

The construction follows the classic reduction from Garey & Johnson:

* Three special vertices form a triangle and represent the three colours
  ``TRUE`` (0), ``FALSE`` (1) and ``BASE`` (2).
* For each variable *x* we create two vertices ``x`` and ``¬x``.  Both are
  adjacent to the ``BASE`` vertex and to each other.  Because they are
  adjacent to ``BASE`` they cannot take the colour of ``BASE``; being
  adjacent to each other forces them to take the two remaining colours –
  one ``TRUE`` and one ``FALSE``.  Which of the two gets ``TRUE`` encodes the
  truth assignment of the variable.
* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we add three new vertices forming a
  triangle.  The *i*‑th vertex of the clause triangle is connected to the
  literal vertex that represents ``ℓᵢ`` (either the ``x`` or ``¬x`` vertex
  created for the variable).  The clause triangle therefore must use all
  three colours.  If all three literals of the clause are false, each of the
  three clause vertices is adjacent to a vertex coloured ``FALSE``; they are
  forced to use only the two colours ``TRUE`` and ``BASE`` – impossible for a
  triangle.  If at least one literal is true, the corresponding clause vertex
  cannot use the colour of that literal, leaving enough freedom to colour the
  triangle with the three distinct colours.

The reduction runs in time linear in the size of the formula, i.e. polynomial
time.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes so that users can run ``problems.ThreeSat.validate``
# on the input if they wish.  The import is optional for the reduction itself.
try:
    from problems import ThreeSat, ThreeColoring  # type: ignore
except Exception:  # pragma: no cover – the module may be imported without the package.
    ThreeSat = None  # type: ignore
    ThreeColoring = None  # type: ignore


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in ``problems.ThreeSat``.

    Returns
    -------
    dict
        A graph instance ``{"n": n, "edges": [[u, v], ...]}`` suitable for
        ``ThreeColoring.validate``.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # input does not conform to the specification.
    if ThreeSat is not None:
        ThreeSat.validate(instance)  # type: ignore[arg-type]

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex indices:
    # 0,1,2 -> the colour triangle (TRUE, FALSE, BASE)
    # For each variable i (1‑based) we allocate two vertices:
    #   var_pos[i]  -> vertex representing literal +i
    #   var_neg[i]  -> vertex representing literal -i
    # For each clause we allocate three vertices forming a triangle.

    # Start counting after the three colour vertices.
    next_vertex = 3
    var_pos: List[int] = [0] * (m + 1)  # index by variable number, ignore 0
    var_neg: List[int] = [0] * (m + 1)

    for i in range(1, m + 1):
        var_pos[i] = next_vertex
        var_neg[i] = next_vertex + 1
        next_vertex += 2

    # Clause vertices: for each clause we store three indices.
    clause_vertices: List[List[int]] = []
    for _ in clauses:
        clause_vertices.append([next_vertex, next_vertex + 1, next_vertex + 2])
        next_vertex += 3

    n = next_vertex  # total number of vertices
    edges: List[List[int]] = []

    # Helper to add an undirected edge (store as [u, v] with u < v for
    # deterministic output – validation does not require ordering.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            raise AssertionError("self‑loop generated in reduction")
        if u > v:
            u, v = v, u
        edges.append([u, v])

    # 1. colour triangle
    add_edge(0, 1)
    add_edge(1, 2)
    add_edge(0, 2)

    # 2. variable gadgets
    for i in range(1, m + 1):
        pos = var_pos[i]
        neg = var_neg[i]
        # edge between the two literals
        add_edge(pos, neg)
        # both literals adjacent to BASE (vertex 2) so they cannot take colour 2
        add_edge(pos, 2)
        add_edge(neg, 2)

    # 3. clause gadgets
    for clause, verts in zip(clauses, clause_vertices):
        c1, c2, c3 = verts
        # triangle among the three clause vertices
        add_edge(c1, c2)
        add_edge(c2, c3)
        add_edge(c3, c1)
        # connect each clause vertex to the literal vertex it represents
        for lit, cv in zip(clause, verts):
            var = abs(lit)
            if lit > 0:
                lit_vertex = var_pos[var]
            else:
                lit_vertex = var_neg[var]
            add_edge(cv, lit_vertex)

    # The reduction is deterministic; we return the instance.
    return {"n": n, "edges": edges}

