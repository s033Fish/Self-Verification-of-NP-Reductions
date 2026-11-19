"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is ``NaeThreeSat`` (not‑all‑equal 3‑SAT) and the target
problem is ``ThreeColoring``. Both problem specifications are described in
``problems.py`` (see the task description). This module provides a single
function ``reduce`` that transforms an instance of NAE‑3‑SAT into an instance
of 3‑Coloring such that the original instance is satisfiable (in the NAE
sense) iff the produced graph is 3‑colorable.

Construction (standard textbook reduction)
-------------------------------------------

* **Base triangle** – three vertices representing the three colours. They are
  connected as a triangle so that any proper 3‑colouring uses three distinct
  colours on them. We call the vertices ``T`` (true), ``F`` (false) and ``N``
  (neutral). Their ids are 0, 1 and 2 respectively.

* **Variable vertices** – for each variable ``x`` we create two vertices
  ``pos_x`` and ``neg_x``. ``pos_x`` will be coloured either ``T`` or ``F`` and
  represents the literal ``+x``; ``neg_x`` is forced to take the opposite colour
  and represents ``-x``.

  To enforce this we add the edges:

  - ``pos_x`` – ``neg_x`` (they must receive different colours)
  - ``pos_x`` – ``N`` and ``neg_x`` – ``N`` (they cannot use the neutral colour,
    therefore each is forced to be either ``T`` or ``F``)

* **Clause gadget** – for each clause ``(l1, l2, l3)`` we create three new
  vertices ``c1, c2, c3`` that form a triangle. Each ``ck`` is connected to the
  vertex representing the corresponding literal ``lk`` (either ``pos_x`` or
  ``neg_x``).

  The triangle ``c1‑c2‑c3`` must use three distinct colours. Because each ``ck``
  is adjacent to its literal vertex, it cannot use the colour assigned to that
  literal. Literals can only be coloured ``T`` or ``F``; consequently the three
  clause vertices must collectively use the colours ``T``, ``F`` and ``N``.
  This is possible **iff** the three literals are not all equal – exactly the
  NAE condition.

The reduction runs in polynomial time: the number of vertices is ``3`` (base)
+ ``2*m`` (variables) + ``3*#clauses`` (clause gadgets) and the number of edges
is linear in the same quantities.

The function returns a dictionary matching the format expected by the
``ThreeColoring`` problem: ``{"n": <num_vertices>, "edges": [[u, v], ...]}``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three literals). Literals are represented as signed integers where a
        positive value ``v`` denotes ``+v`` and a negative value ``-v`` denotes
        ``-v``.

    Returns
    -------
    dict
        A graph instance for the ``ThreeColoring`` problem.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Base triangle vertices: 0 = T, 1 = F, 2 = N
    base_T, base_F, base_N = 0, 1, 2
    edges.extend([[base_T, base_F], [base_F, base_N], [base_N, base_T]])

    # Variable vertices: for each variable i (1‑based) we allocate two ids
    # pos_i = 3 + 2*(i-1), neg_i = pos_i + 1
    pos_ids: List[int] = []  # index i‑1 -> vertex id for +i
    neg_ids: List[int] = []
    for i in range(1, m + 1):
        pos_id = 3 + 2 * (i - 1)
        neg_id = pos_id + 1
        pos_ids.append(pos_id)
        neg_ids.append(neg_id)
        # Edge between pos and neg (different colours)
        edges.append([pos_id, neg_id])
        # Connect both to the neutral vertex to forbid colour N
        edges.append([pos_id, base_N])
        edges.append([neg_id, base_N])

    # Helper to map a literal to the corresponding vertex id
    def literal_vertex(lit: int) -> int:
        var = abs(lit)
        if var == 0 or var > m:
            raise ValueError("Literal refers to non‑existent variable")
        if lit > 0:
            return pos_ids[var - 1]
        else:
            return neg_ids[var - 1]

    # Clause gadgets
    # Starting id after variables
    next_id = 3 + 2 * m
    for clause in clauses:
        if len(clause) != 3:
            raise ValueError("Each clause must have exactly three literals")
        # Create three vertices for the clause
        c_vertices = [next_id, next_id + 1, next_id + 2]
        next_id += 3
        # Form a triangle among them
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])
        # Connect each clause vertex to the vertex representing the literal
        for cv, lit in zip(c_vertices, clause):
            lit_v = literal_vertex(lit)
            edges.append([cv, lit_v])

    # Remove duplicate edges (the construction may add the same edge twice)
    # Store edges as sorted tuples in a set for uniqueness.
    edge_set = {tuple(sorted(e)) for e in edges}
    unique_edges = [list(e) for e in edge_set]

    return {"n": next_id, "edges": unique_edges}

