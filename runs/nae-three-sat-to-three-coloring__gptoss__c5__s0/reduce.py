"""Reduction from NAE-3-SAT to 3-Coloring.

The reduction follows the classic construction using three colours:
    * colour 0 – the *base* colour (often denoted B)
    * colour 1 – truth colour (T)
    * colour 2 – false colour (F)

For each variable *x* we create two vertices ``x`` and ``~x`` that together
with the base vertex form a triangle.  In any proper 3‑colouring the base
vertex receives colour 0, forcing the two literal vertices to receive the
remaining two colours (one T and one F).  The assignment of truth values is
read off from which of the two vertices receives colour 1.

For each clause (ℓ₁,ℓ₂,ℓ₃) we create a triangle of *clause vertices*
``c₁, c₂, c₃``.  Vertex ``cᵢ`` is connected to the literal vertex that
represents ℓᵢ (positive literal → the ``x`` vertex, negative literal → the
``~x`` vertex).  The three clause vertices are also pairwise adjacent,
forming a triangle.

If all three literals of a clause receive the same truth colour, then each
clause vertex is forbidden from using that colour (because it is adjacent to
its literal vertex).  Only two colours remain for three mutually adjacent
vertices – impossible.  Conversely, if the clause contains at least one true
and at least one false literal, the three clause vertices can be coloured
properly (e.g. use the base colour for the vertex whose literal has colour 1,
and the remaining two colours for the other two vertices).

Thus the constructed graph is 3‑colourable iff the original NAE‑3‑SAT formula
has a not‑all‑equal satisfying assignment.

The implementation below builds this graph and returns it in the format
required by :class:`ThreeColoring` (a dict with keys ``"n"`` and ``"edges"``).
"""

from __future__ import annotations

from typing import List, Dict, Tuple

from problems import NaeThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary representing a NAE‑3‑SAT instance as defined in
        ``problems.NaeThreeSat``.

    Returns
    -------
    dict
        A graph ``{"n": n, "edges": [[u, v], ...]}`` suitable for the
        ``ThreeColoring`` problem.
    """
    # Validate the input according to the source problem definition.
    NaeThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering scheme:
    #   0                     – base vertex (colour B)
    #   1 .. 2*num_vars       – literal vertices, two per variable.
    #   after that            – clause vertices, three per clause.
    # For variable i (1‑based), the positive literal vertex is
    #   pos = 1 + 2*(i-1)
    # and the negative literal vertex is
    #   neg = pos + 1
    edges: List[Tuple[int, int]] = []

    # Helper to add an undirected edge without duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            raise AssertionError("self‑loop attempted in reduction")
        if u > v:
            u, v = v, u
        edges.append((u, v))

    base = 0
    # Variable gadgets.
    for i in range(1, num_vars + 1):
        pos = 1 + 2 * (i - 1)
        neg = pos + 1
        # Triangle base‑pos‑neg
        add_edge(base, pos)
        add_edge(base, neg)
        add_edge(pos, neg)

    # Clause gadgets.
    next_vertex = 1 + 2 * num_vars  # first free id for clause vertices
    for clause in clauses:
        # clause has exactly three literals
        clause_vertices = []
        for lit in clause:
            var = abs(lit)
            # Determine the literal vertex for this literal.
            pos = 1 + 2 * (var - 1)
            neg = pos + 1
            lit_vertex = pos if lit > 0 else neg
            # Create a new clause vertex.
            cv = next_vertex
            next_vertex += 1
            clause_vertices.append(cv)
            # Connect clause vertex to the corresponding literal vertex.
            add_edge(cv, lit_vertex)
        # Connect the three clause vertices into a triangle.
        a, b, c = clause_vertices
        add_edge(a, b)
        add_edge(b, c)
        add_edge(c, a)

    # Remove possible duplicate edges (the construction should not create any,
    # but we deduplicate to be safe).
    unique_edges = list({frozenset(e) for e in edges})
    edge_list = [list(e) for e in unique_edges]

    n_vertices = next_vertex  # total number of vertices created
    return {"n": n_vertices, "edges": edge_list}

