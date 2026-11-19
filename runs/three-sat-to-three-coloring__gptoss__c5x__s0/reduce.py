"""Reduction from 3‑SAT to 3‑Coloring.

The reduction follows the classic textbook construction:

* Introduce three special vertices representing the three colours:
  - ``TRUE`` (index 0)
  - ``FALSE`` (index 1)
  - ``BASE`` (index 2)
  These three vertices form a triangle, forcing any proper 3‑colouring to
  assign them three distinct colours.

* For each Boolean variable ``x_i`` we create two vertices ``x_i`` and
  ``¬x_i``.  Both are connected to ``BASE`` (so they cannot take the BASE
  colour) and they are connected to each other.  Consequently each of the
  two vertices must be coloured either ``TRUE`` or ``FALSE`` and they must
  receive different colours – this encodes a truth assignment for the
  variable.

* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we create a triangle of three fresh
  vertices ``c₁, c₂, c₃``.  Vertex ``c_k`` is connected to the literal
  vertex that corresponds to ``ℓ_k`` (the positive or negative variable
  vertex).  The three clause vertices are also mutually connected, forming a
  triangle.  If all three literals are coloured ``FALSE`` then each clause
  vertex is forbidden to use the colour ``FALSE`` and therefore only two
  colours remain for a triangle – impossible.  If at least one literal is
  coloured ``TRUE`` the triangle can be coloured using the three colours.

The construction runs in polynomial time and the resulting graph is
3‑colourable iff the original formula is satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dict representing a 3‑SAT formula as described in ``ThreeSat``.

    Returns
    -------
    dict
        A graph instance suitable for ``ThreeColoring.validate``.
    """
    # Validate the source instance first (will raise if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Special colour vertices: 0 = TRUE, 1 = FALSE, 2 = BASE
    TRUE, FALSE, BASE = 0, 1, 2
    # Triangle among the three special vertices
    edges.append([TRUE, FALSE])
    edges.append([FALSE, BASE])
    edges.append([BASE, TRUE])

    # Helper to compute indices of literal vertices
    def pos_index(var: int) -> int:
        """Return vertex index for the positive literal of variable ``var``.
        Variables are numbered from 1..m.
        """
        return 3 + 2 * (var - 1)

    def neg_index(var: int) -> int:
        """Return vertex index for the negative literal of variable ``var``.
        """
        return 3 + 2 * (var - 1) + 1

    # Variable gadgets
    for var in range(1, m + 1):
        p = pos_index(var)
        n = neg_index(var)
        # Edge between the two literals (they must receive different colours)
        edges.append([p, n])
        # Both literals are adjacent to BASE so they cannot take the BASE colour
        edges.append([p, BASE])
        edges.append([n, BASE])

    # Clause gadgets
    next_vertex = 3 + 2 * m  # first free index after variable vertices
    for clause in clauses:
        # clause has exactly three literals
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        # triangle among clause vertices
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])

        # connect each clause vertex to the appropriate literal vertex
        for lit, c_v in zip(clause, c_vertices):
            var = abs(lit)
            if lit > 0:
                lit_vertex = pos_index(var)
            else:
                lit_vertex = neg_index(var)
            edges.append([c_v, lit_vertex])

        next_vertex += 3

    # Build the final instance dict
    graph_instance: Dict = {"n": next_vertex, "edges": edges}
    # Validate the target instance before returning (ensures we didn't make a mistake)
    ThreeColoring.validate(graph_instance)
    return graph_instance

