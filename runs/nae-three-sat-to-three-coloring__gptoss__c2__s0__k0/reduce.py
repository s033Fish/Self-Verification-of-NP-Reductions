"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (NAE-3-SAT) is defined in ``problems.py`` as ``NaeThreeSat``
with instances of the form ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.
Each literal ``l`` is an integer ``+v`` (positive) or ``-v`` (negative) where
``v`` is a 1‑based variable index.

The target problem (3‑Coloring) expects an instance ``{"n": n, "edges": [[u, v], ...]}``
with vertices ``0 .. n-1`` and undirected edges.

The construction follows the classic polynomial‑time reduction:

* Create a distinguished triangle of three vertices (0, 1, 2).  These will
  represent the three colours used by the 3‑colouring algorithm.
* For each variable ``v`` (1‑based) introduce two vertices ``pos_v`` and
  ``neg_v``.  Both are connected to vertex ``0`` (the "base" colour) and to each
  other.  In any proper 3‑colouring, ``pos_v`` and ``neg_v`` must receive the two
  non‑base colours, thereby encoding a truth assignment (e.g. colour 1 = true,
  colour 2 = false).
* For each clause ``(ℓ1, ℓ2, ℓ3)`` add three fresh vertices ``a, b, c`` that form a
  triangle.  Connect ``a`` to the vertex representing literal ``ℓ1``, ``b`` to
  ``ℓ2`` and ``c`` to ``ℓ3``.  The triangle forces the three literals not to be
  coloured identically: if they were, the three new vertices would have only two
  colours available (the base colour and the opposite non‑base colour) and a
  triangle cannot be 2‑coloured.

The resulting graph is 3‑colourable iff the original NAE‑3‑SAT formula is
satisfiable.  The construction runs in time linear in the size of the input
formula.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described in
        the problem statement.

    Returns
    -------
    dict
        A graph instance for the 3‑Coloring problem.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges_set = set()  # type: set[Tuple[int, int]]

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        # store edges with ordered tuple to avoid duplicates
        if u > v:
            u, v = v, u
        edges_set.add((u, v))

    # 1. Base triangle vertices 0,1,2
    add_edge(0, 1)
    add_edge(1, 2)
    add_edge(2, 0)

    next_id = 3  # next free vertex id

    # 2. Variable literal vertices
    # Maps literal integer (+v or -v) to vertex id
    literal_to_vertex: Dict[int, int] = {}
    for v in range(1, m + 1):
        pos_id = next_id
        next_id += 1
        neg_id = next_id
        next_id += 1
        # connect each to the base vertex 0 and to each other
        add_edge(pos_id, neg_id)
        add_edge(pos_id, 0)
        add_edge(neg_id, 0)
        literal_to_vertex[v] = pos_id   # +v
        literal_to_vertex[-v] = neg_id  # -v

    # 3. Clause gadgets
    for clause in clauses:
        if len(clause) != 3:
            # According to the specification clauses always have size 3,
            # but we guard against malformed input.
            continue
        # create three new vertices for the clause triangle
        a = next_id
        b = next_id + 1
        c = next_id + 2
        next_id += 3
        # triangle among a,b,c
        add_edge(a, b)
        add_edge(b, c)
        add_edge(c, a)
        # connect each to the appropriate literal vertex
        l1, l2, l3 = clause
        add_edge(a, literal_to_vertex[l1])
        add_edge(b, literal_to_vertex[l2])
        add_edge(c, literal_to_vertex[l3])

    # Convert edge set to required list format
    edges = [[u, v] for (u, v) in edges_set]
    n = next_id  # total number of vertices created
    return {"n": n, "edges": edges}

