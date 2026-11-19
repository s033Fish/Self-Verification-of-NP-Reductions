"""Reduction from NAE-3-SAT to 3-Coloring.

The reduction works in two stages:

1. **NAE‑3‑SAT → 3‑SAT** –  A NAE clause (l₁,l₂,l₃) is satisfied iff the
   three literals are not all equal.  This is equivalent to the conjunction
   of the two ordinary 3‑SAT clauses ``(l₁ ∨ l₂ ∨ l₃)`` and
   ``(¬l₁ ∨ ¬l₂ ∨ ¬l₃)``.  Hence we replace every NAE clause by those two
   clauses.

2. **3‑SAT → 3‑Coloring** –  We use the classic polynomial‑time reduction
   described in many textbooks (e.g. Garey & Johnson).  The target graph
   contains three special vertices that form a triangle; they represent the
   colours *True*, *False* and *Base*.  For each variable ``v`` we create two
   vertices ``v⁺`` and ``v⁻`` (positive and negative literal).  Both are
   adjacent to the *Base* vertex and to each other, forcing exactly one of
   them to take the *True* colour and the other the *False* colour.

   For each 3‑SAT clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we add a clause‑gadget consisting
   of three new vertices that form a triangle.  The i‑th vertex of the
   gadget is connected to the literal vertex that would satisfy the clause
   when that literal is coloured *True*.  If all three literals were *False*
   the three gadget vertices would be forced to the *Base* colour, which is
   impossible because they are pairwise adjacent.  Consequently at least one
   literal of the clause must be *True*.

The composition of the two stages yields a polynomial‑time many‑one
reduction from ``NaeThreeSat`` to ``ThreeColoring``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import NaeThreeSat, ThreeColoring

def _validate_source(instance: Dict) -> None:
    """Validate the NAE‑3‑SAT instance using the provided class.

    ``NaeThreeSat.validate`` raises ``InvalidInstance`` on malformed input.
    The function is separated only for readability.
    """

    NaeThreeSat.validate(instance)


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    The returned graph is guaranteed to be 3‑colorable **iff** the original
    formula has a not‑all‑equal satisfying assignment.
    """

    _validate_source(instance)

    num_vars: int = instance["num_vars"]
    nae_clauses: List[List[int]] = instance["clauses"]

    # ------------------------------------------------------------------
    # Stage 1 – convert to an ordinary 3‑SAT instance.
    # ------------------------------------------------------------------
    sat_clauses: List[List[int]] = []
    for clause in nae_clauses:
        # original clause
        sat_clauses.append(clause[:])
        # negated clause – flip sign of each literal
        sat_clauses.append([-lit for lit in clause])

    # ------------------------------------------------------------------
    # Stage 2 – build the 3‑Coloring graph.
    # ------------------------------------------------------------------
    edges: List[List[int]] = []

    # Base triangle vertices: 0 = True, 1 = False, 2 = Base.
    TRUE, FALSE, BASE = 0, 1, 2
    # triangle among them
    edges.extend([[TRUE, FALSE], [FALSE, BASE], [BASE, TRUE]])

    # Mapping from variable index to (pos_vertex, neg_vertex)
    var_pos: List[int] = [0] * (num_vars + 1)  # 1‑based indexing
    var_neg: List[int] = [0] * (num_vars + 1)

    next_vid = 3  # next free vertex id after the base triangle
    for v in range(1, num_vars + 1):
        pos = next_vid
        neg = next_vid + 1
        next_vid += 2
        var_pos[v] = pos
        var_neg[v] = neg

        # Connect each literal vertex to the BASE vertex
        edges.append([pos, BASE])
        edges.append([neg, BASE])
        # Edge between the two literals forces opposite colours
        edges.append([pos, neg])

    # Clause gadgets for each 3‑SAT clause
    for clause in sat_clauses:
        # Create three new vertices for the clause triangle
        c1 = next_vid
        c2 = next_vid + 1
        c3 = next_vid + 2
        next_vid += 3
        # triangle among them
        edges.extend([[c1, c2], [c2, c3], [c3, c1]])

        # Connect each clause‑vertex to the corresponding literal vertex
        literals = clause
        for lit, cv in zip(literals, (c1, c2, c3)):
            if lit > 0:
                literal_vertex = var_pos[lit]
            else:
                literal_vertex = var_neg[-lit]
            edges.append([cv, literal_vertex])

    graph: Dict = {"n": next_vid, "edges": edges}
    # Validate the produced graph using the target class (helps catch bugs).
    ThreeColoring.validate(graph)
    return graph

