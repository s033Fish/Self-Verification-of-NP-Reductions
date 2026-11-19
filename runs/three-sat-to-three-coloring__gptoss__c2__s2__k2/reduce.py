"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined by :class:`ThreeSat` in ``problems.py``.  An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal is an integer ``+v`` (variable *v* is true) or ``-v``
*(v* is false).

The target problem is :class:`ThreeColoring`.  An instance is a graph given as
``{"n": n, "edges": [[u, v], ...]}`` where vertices are numbered ``0`` …
``n‑1``.

We implement the classic polynomial‑time reduction (Karp, 1972).  The idea is
to force any proper 3‑colouring to correspond to a satisfying assignment:

* Three special vertices ``T``, ``F`` and ``B`` form a triangle.  In any
  proper 3‑colouring they receive three distinct colours – we interpret the
  colours as *True*, *False* and a *base* colour.
* For each variable *x* we create two vertices ``x`` and ``¬x``.  Both are
  adjacent to the base vertex ``B`` and to each other.  Consequently they must
  be coloured ``T`` and ``F`` (in some order).  The vertex coloured ``T``
  represents the literal that evaluates to true.
* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we create three new vertices forming a
  triangle.  The *i*‑th vertex of the clause triangle is adjacent to the
  literal vertex that corresponds to ``ℓᵢ``.  Because adjacent vertices must have
  different colours, a clause vertex cannot use the colour of the literal it
  is linked to.  If all three literals are false, the three clause vertices are
  forbidden from using the colour ``F``; they would then be limited to the two
  remaining colours ``T`` and ``B`` – impossible for a triangle.  Hence at
  least one literal must be true, which exactly matches clause satisfaction.

The construction runs in time linear in the size of the SAT instance and
produces a graph whose 3‑colourability is equivalent to the formula's
 satisfiability.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation (optional but helpful).
from problems import ThreeSat, ThreeColoring


def _add_edge(edges: List[List[int]], u: int, v: int) -> None:
    """Append an undirected edge ``[u, v]`` (order does not matter)."""
    if u == v:
        raise ValueError("self‑loops are not allowed in the reduction")
    edges.append([u, v])


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    The returned graph is 3‑colourable iff the SAT formula is satisfiable.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed.  The problem statement does not require us to catch
    # the exception, so we let it propagate.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # ---------------------------------------------------------------------
    # 1. Base triangle (vertices 0, 1, 2).
    #    0 -> True, 1 -> False, 2 -> Base.
    # ---------------------------------------------------------------------
    TRUE, FALSE, BASE = 0, 1, 2
    _add_edge(edges, TRUE, FALSE)
    _add_edge(edges, TRUE, BASE)
    _add_edge(edges, FALSE, BASE)

    # ---------------------------------------------------------------------
    # 2. Variable vertices.  For each variable i we create two vertices:
    #    pos_i  (positive literal) and neg_i (negative literal).
    #    Both are adjacent to BASE and to each other.
    # ---------------------------------------------------------------------
    # Store mapping from literal value (+i / -i) to the vertex index.
    literal_to_vertex: Dict[int, int] = {}
    next_vertex = 3  # after the base triangle
    for var in range(1, m + 1):
        pos = next_vertex
        neg = next_vertex + 1
        next_vertex += 2

        # Edge between the literal pair and to the BASE vertex.
        _add_edge(edges, pos, neg)
        _add_edge(edges, pos, BASE)
        _add_edge(edges, neg, BASE)

        literal_to_vertex[var] = pos   # +var
        literal_to_vertex[-var] = neg  # -var

    # ---------------------------------------------------------------------
    # 3. Clause gadgets.
    #    For each clause we add three vertices forming a triangle.  The i‑th
    #    vertex of the clause triangle connects to the vertex representing the
    #    i‑th literal of the clause.
    # ---------------------------------------------------------------------
    for clause in clauses:
        # clause is a list of three literals, each distinct by definition.
        clause_vertices = []
        for _ in range(3):
            clause_vertices.append(next_vertex)
            next_vertex += 1

        # Connect the three clause vertices in a triangle.
        a, b, c = clause_vertices
        _add_edge(edges, a, b)
        _add_edge(edges, b, c)
        _add_edge(edges, c, a)

        # Connect each clause vertex to the appropriate literal vertex.
        for lit, cv in zip(clause, clause_vertices):
            literal_vertex = literal_to_vertex[lit]
            _add_edge(edges, cv, literal_vertex)

    # ---------------------------------------------------------------------
    # Construct the final graph instance.
    # ---------------------------------------------------------------------
    n_vertices = next_vertex  # vertices are 0 .. next_vertex-1
    result: Dict[str, Any] = {"n": n_vertices, "edges": edges}

    # Optional validation of the target instance – ensures we produced a
    # well‑formed graph.
    ThreeColoring.validate(result)
    return result

