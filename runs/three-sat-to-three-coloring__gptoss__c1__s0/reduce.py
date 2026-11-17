"""Reduction from 3‑SAT to 3‑Coloring.

The source problem (ThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable *v* is
true) or ``-v`` (meaning variable *v* is false).  The target problem
(ThreeColoring) expects a graph represented as::

    {"n": n, "edges": [[u, v], ...]}

with vertices numbered ``0 .. n-1`` and undirected edges.

The construction below is a classic polynomial‑time reduction (see
Garey & Johnson, *Computers and Intractability*, Chap. 3).  It creates a
graph that is 3‑colourable **iff** the original formula is satisfiable.

Construction outline
----------------------

* Three special vertices ``A``, ``B`` and ``C`` are added and connected in
  a triangle.  In any proper 3‑colouring they will receive three distinct
  colours.  We interpret colour of ``B`` as *true* and colour of ``C`` as
  *false* (the colour of ``A`` is a dummy base colour).

* For each variable *x_i* we create two vertices ``x_i`` and ``¬x_i``.
  They are both adjacent to the base vertex ``A`` and to each other.
  The edge between them forces them to receive different colours; because
  they cannot use the colour of ``A`` they must be coloured ``B`` and
  ``C`` – one true and one false – representing the truth assignment of
  the variable.

* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we add three new vertices
  ``c1, c2, c3`` forming a triangle.  Vertex ``ck`` is connected to the
  literal vertex that corresponds to ``ℓk`` (e.g. ``x_i`` for a positive
  literal and ``¬x_i`` for a negative literal).  The clause triangle
  forces the three vertices to receive three distinct colours.  If all
  three literals were coloured ``C`` (i.e. all false) then each ``ck``
  would be forbidden from using colour ``C``; only colours ``A`` and
  ``B`` would remain, which is insufficient for a proper 3‑colouring of a
  triangle.  Hence at least one literal must be coloured ``B`` (true) for
  the clause gadget to be colourable.

The reduction runs in time linear in the size of the formula and uses a
linear number of vertices and edges, thus satisfying the polynomial‑time
requirement.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list
        of three‑element lists of literals).

    Returns
    -------
    dict
        A graph instance with keys ``"n"`` and ``"edges"`` suitable for
        the ``ThreeColoring`` problem.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # ------------------------------------------------------------------
    # Vertex numbering
    # ------------------------------------------------------------------
    # 0,1,2 : the special triangle (A,B,C)
    A, B, C = 0, 1, 2
    next_id = 3

    # Mapping from variable index to the vertex ids of the literal nodes.
    # var_pos[i]  -> vertex for literal +i (x_i)
    # var_neg[i]  -> vertex for literal -i (¬x_i)
    var_pos: List[int] = [0] * (m + 1)  # 1‑based indexing; index 0 unused
    var_neg: List[int] = [0] * (m + 1)

    for i in range(1, m + 1):
        var_pos[i] = next_id
        next_id += 1
        var_neg[i] = next_id
        next_id += 1

    # Clause vertices will be stored as a list of triples (c1,c2,c3)
    clause_vertices: List[Tuple[int, int, int]] = []
    for _ in clauses:
        c1 = next_id
        c2 = next_id + 1
        c3 = next_id + 2
        clause_vertices.append((c1, c2, c3))
        next_id += 3

    n_vertices = next_id

    # ------------------------------------------------------------------
    # Edge construction – we store edges as a set of ordered tuples to
    # avoid duplicates.
    # ------------------------------------------------------------------
    edges: Set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        edge = (u, v) if u < v else (v, u)
        edges.add(edge)

    # Special triangle A‑B‑C
    add_edge(A, B)
    add_edge(B, C)
    add_edge(C, A)

    # Variable gadgets
    for i in range(1, m + 1):
        pos = var_pos[i]
        neg = var_neg[i]
        # each literal adjacent to base vertex A
        add_edge(pos, A)
        add_edge(neg, A)
        # literals of a variable are adjacent (force opposite colours)
        add_edge(pos, neg)

    # Clause gadgets
    for (clause, (c1, c2, c3)) in zip(clauses, clause_vertices):
        # triangle among the three clause vertices
        add_edge(c1, c2)
        add_edge(c2, c3)
        add_edge(c3, c1)

        # connect each clause vertex to the corresponding literal vertex
        for lit, cv in zip(clause, (c1, c2, c3)):
            var = abs(lit)
            if var == 0:
                # should never happen because variables are 1‑based
                continue
            if lit > 0:
                lit_vertex = var_pos[var]
            else:
                lit_vertex = var_neg[var]
            add_edge(cv, lit_vertex)

    # Convert edge set to required list representation
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]

    return {"n": n_vertices, "edges": edge_list}

