"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (NAE-3-SAT) is defined in ``problems.py`` as the class
``NaeThreeSat``.  An instance is a dictionary with keys ``"num_vars"`` and
``"clauses"`` where each clause is a list of three literals ``+v`` or ``-v``.

The target problem (3‑Coloring) is defined as the class ``ThreeColoring``.
Its instance format is a dictionary ``{"n": n, "edges": [[u, v], ...]}`` where
vertices are numbered ``0 .. n-1`` and each edge connects two distinct vertices.

The reduction follows a classic construction:

* Introduce a special vertex ``C`` (vertex ``0``) that will be forced to take the
  third colour.
* For each variable ``i`` (1‑based) create a vertex ``v_i`` connected to ``C``.
  This forces ``v_i`` to be coloured either colour ``T`` (true) or colour ``F``
  (false).
* For each variable also create a *negated* vertex ``n_i``.  It is connected to
  ``C`` **and** to ``v_i``.  Consequently ``n_i`` must take the opposite colour
  of ``v_i`` (it cannot be the third colour because of the edge to ``C``).
* For each clause ``(ℓ1, ℓ2, ℓ3)`` we add a triangle of fresh vertices
  ``a, b, c``.  The three literals are linked to the triangle vertices:
  ``ℓ1`` to ``a``, ``ℓ2`` to ``b`` and ``ℓ3`` to ``c``.
  The triangle forces its three vertices to receive three distinct colours.
  Because each of them is adjacent to the corresponding literal vertex, a
  literal cannot share the colour of its neighbour.  If all three literals had
  the same colour (all true or all false) the triangle would have only two
  colours available for its three vertices – impossible.  Hence a proper
  3‑colouring exists iff each clause contains at least one true and at least
  one false literal, i.e. the NAE condition.

The construction runs in polynomial time and respects all edge‑case
requirements (empty formula, zero variables, etc.).
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation; the reduction itself does not
# depend on any solver functionality.
from problems import NaeThreeSat, ThreeColoring


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``NaeThreeSat`` specification.

    Returns
    -------
        A dictionary adhering to the ``ThreeColoring`` specification such that
        the graph is 3‑colourable **iff** the original formula is NAE‑satisfiable.
    """
    # Validate the input to guarantee the expected format.
    NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Vertex 0 is the special "third‑colour" vertex C.
    # Vertices 1 .. m   : variable vertices v_i
    # Vertices m+1 .. 2m: negated vertices n_i
    base = 0

    # Connect each variable vertex to the base vertex.
    for i in range(m):
        v = 1 + i
        edges.append([base, v])

    # Create negated vertices and connect them to both the base and the
    # corresponding variable vertex.
    for i in range(m):
        v = 1 + i
        n = 1 + m + i
        edges.append([base, n])   # forbids colour of the third vertex
        edges.append([v, n])      # forces opposite colour to v

    # Index of the next fresh vertex after the base, variables and negated
    # vertices.
    next_vertex = 1 + 2 * m

    for clause in clauses:
        # Each clause is guaranteed to have exactly three literals.
        lit_vertices: List[int] = []
        for lit in clause:
            var_index = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                # Positive literal uses the variable vertex.
                lit_vertices.append(1 + var_index)
            else:
                # Negative literal uses the negated vertex.
                lit_vertices.append(1 + m + var_index)

        # Create the triangle vertices a, b, c for this clause.
        a = next_vertex
        b = next_vertex + 1
        c = next_vertex + 2
        next_vertex += 3

        # Triangle edges (a‑b‑c‑a).
        edges.append([a, b])
        edges.append([b, c])
        edges.append([c, a])

        # Connect each literal vertex to its dedicated triangle vertex.
        edges.append([lit_vertices[0], a])
        edges.append([lit_vertices[1], b])
        edges.append([lit_vertices[2], c])

    n = next_vertex  # total number of vertices
    # Validate the constructed graph before returning (optional but helpful).
    ThreeColoring.validate({"n": n, "edges": edges})
    return {"n": n, "edges": edges}

