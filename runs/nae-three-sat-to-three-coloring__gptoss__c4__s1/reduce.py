"""Reduction from NAE-3-SAT to 3-Coloring.

The construction follows the standard polynomial‑time reduction:

* A base triangle with vertices representing the three colours (TRUE, FALSE,
  AUX).  These three vertices are numbered 0, 1, 2 and are pairwise
  adjacent.
* For each variable *i* we create two vertices ``pos_i`` and ``neg_i``.
  Both are adjacent to the AUX vertex (2) and to each other.  Consequently
  they can only be coloured 0 or 1 and must receive opposite colours –
  encoding the truth value of the variable.
* For each clause (ℓ₁,ℓ₂,ℓ₃) we add three new vertices a, b, c forming a
  triangle.  Vertex a is adjacent to the vertex representing literal ℓ₁
  (``pos`` if the literal is positive, ``neg`` otherwise), and similarly for
  b and c.  The triangle forces the three auxiliary vertices to receive three
  distinct colours.  This is possible exactly when the three literals are not
  all assigned the same truth value, which is the NAE condition.

The resulting graph is 3‑colourable iff the original NAE‑3‑SAT instance is
satisfiable.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import NaeThreeSat, ThreeColoring


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a NAE‑3‑SAT instance into an equivalent 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``NaeThreeSat`` specification.

    Returns
    -------
    dict
        A dictionary adhering to the ``ThreeColoring`` specification such
        that the graph is 3‑colourable iff the NAE‑3‑SAT formula is
        satisfiable.
    """
    # Validate source instance.
    NaeThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering:
    # 0,1,2 -> base triangle (TRUE, FALSE, AUX)
    # For each variable i (1‑based): pos_i, neg_i
    # Then clause auxiliary vertices.
    edges: List[List[int]] = []

    # base triangle edges
    edges.append([0, 1])
    edges.append([1, 2])
    edges.append([0, 2])

    # Keep track of vertex ids for variable literals
    pos_id = {}
    neg_id = {}
    next_id = 3  # next free vertex number after base triangle
    for i in range(1, num_vars + 1):
        pid = next_id
        nid = next_id + 1
        pos_id[i] = pid
        neg_id[i] = nid
        # edges to AUX (2)
        edges.append([pid, 2])
        edges.append([nid, 2])
        # edge between pos and neg to force opposite colours
        edges.append([pid, nid])
        next_id += 2

    # Clause gadgets
    for clause in clauses:
        # create three auxiliary vertices a,b,c
        a = next_id
        b = next_id + 1
        c = next_id + 2
        next_id += 3
        # triangle among them
        edges.append([a, b])
        edges.append([b, c])
        edges.append([c, a])
        # connect each to the appropriate literal vertex
        lits = clause
        for lit, aux in zip(lits, (a, b, c)):
            var = abs(lit)
            if lit > 0:
                lit_vertex = pos_id[var]
            else:
                lit_vertex = neg_id[var]
            edges.append([aux, lit_vertex])

    n = next_id  # total number of vertices created
    return {"n": n, "edges": edges}

