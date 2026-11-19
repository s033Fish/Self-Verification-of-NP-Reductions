"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal is an integer ``+v`` (variable *v* is true) or ``-v``
(variable *v* is false).

The target problem is ``ThreeColoring`` with the instance format:

    {"n": n, "edges": [[u, v], ...]}

The reduction follows the classic polynomial‑time construction used in many
textbooks:

* Three special vertices – ``T``, ``F`` and ``B`` – form a triangle.  In any
  proper 3‑coloring they receive three distinct colours.  We treat colour 0
  (the colour of ``T``) as *true*, colour 1 (the colour of ``F``) as *false*
  and colour 2 (the colour of ``B``) as a *base* colour that literal vertices
  are not allowed to use.
* For each variable ``x`` we create two vertices ``x`` (positive literal) and
  ``¬x`` (negative literal).  Both are adjacent to ``B`` so they cannot take
  the base colour.  An edge between the two literals forces them to receive
  opposite colours, i.e. one true and the other false.
* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a triangle of three new
  vertices ``c1, c2, c3``.  Vertex ``ci`` is connected to the literal vertex
  representing ``ℓi``.  The clause triangle can be properly coloured iff at
  least one of the three literals is coloured true; otherwise the three
  clause vertices would be forced to use only the two colours *true* and
  *false*, which is impossible for a triangle.

The construction runs in time linear in the size of the 3‑SAT instance and
produces a graph whose 3‑colourability exactly matches satisfiability of the
original formula.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        length‑3 literal lists).  Literals are integers ``+v`` or ``-v`` as
        described in the problem statement.

    Returns
    -------
    dict
        A graph instance ``{"n": n, "edges": [[u, v], ...]}`` suitable for
        the ``ThreeColoring`` problem.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    edges: List[List[int]] = []

    # ------------------------------------------------------------
    # 0,1,2 are the three special vertices forming a triangle.
    # They guarantee three distinct colours.
    # ------------------------------------------------------------
    SPECIAL_T, SPECIAL_F, SPECIAL_B = 0, 1, 2
    edges.append([SPECIAL_T, SPECIAL_F])
    edges.append([SPECIAL_T, SPECIAL_B])
    edges.append([SPECIAL_F, SPECIAL_B])

    # ------------------------------------------------------------
    # Map each literal to a vertex index.
    # Positive literal of variable i -> pos_id
    # Negative literal of variable i -> neg_id
    # Indices start after the three special vertices.
    # ------------------------------------------------------------
    literal_vertex: Dict[int, int] = {}
    next_id = 3  # first free vertex id after the specials
    for var in range(1, m + 1):
        pos_id = next_id
        neg_id = next_id + 1
        next_id += 2

        # Store mapping: +v -> pos_id, -v -> neg_id
        literal_vertex[+var] = pos_id
        literal_vertex[-var] = neg_id

        # Literal vertices cannot use the base colour (SPECIAL_B)
        edges.append([pos_id, SPECIAL_B])
        edges.append([neg_id, SPECIAL_B])

        # Positive and negative literals must receive opposite colours.
        edges.append([pos_id, neg_id])

    # ------------------------------------------------------------
    # Clause gadgets.
    # For each clause we add three new vertices forming a triangle.
    # Each vertex of the triangle is connected to the corresponding
    # literal vertex.
    # ------------------------------------------------------------
    for clause in clauses:
        if len(clause) != 3:
            # The specification guarantees exactly three literals, but we
            # guard against malformed input.
            raise ValueError("Each clause must contain exactly three literals")

        # Create three clause vertices.
        c_ids = [next_id, next_id + 1, next_id + 2]
        next_id += 3

        # Form the triangle among them.
        edges.append([c_ids[0], c_ids[1]])
        edges.append([c_ids[1], c_ids[2]])
        edges.append([c_ids[2], c_ids[0]])

        # Connect each clause vertex to the appropriate literal vertex.
        for ci, lit in zip(c_ids, clause):
            lit_vertex = literal_vertex.get(lit)
            if lit_vertex is None:
                # This can happen if a variable appears in a clause but the
                # formula declared fewer variables.  We treat it as an error
                # because the instance would be invalid.
                raise ValueError(f"Literal {lit} refers to undefined variable")
            edges.append([ci, lit_vertex])

    # ------------------------------------------------------------
    # Build the final instance dictionary.
    # ------------------------------------------------------------
    n = next_id  # total number of vertices used
    # Ensure edges are undirected and each appears only once (order does not
    # matter for the verifier, but we canonicalise them for cleanliness).
    canonical_edges = []
    seen = set()
    for u, v in edges:
        if u == v:
            continue  # ignore self loops (should not happen)
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            canonical_edges.append([a, b])

    return {"n": n, "edges": canonical_edges}

