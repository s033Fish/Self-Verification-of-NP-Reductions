"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is a string ``"+v"`` (variable ``v`` true) or
``"-v"`` (variable ``v`` false).  Every clause contains exactly three
different variables.

The target problem is ``IndependentSet`` with an instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction follows the classic textbook construction:

* For each clause we create a triangle of three vertices – one vertex for
  each literal.  Edges inside a clause ensure that an independent set can
  contain **at most** one vertex from each clause.
* Vertices representing contradictory literals (``+v`` and ``-v``) are
  connected by an edge.  This guarantees that an independent set cannot pick
  both a literal and its negation.
* We ask for an independent set of size ``k = number_of_clauses``.  Such a
  set exists iff the original formula is satisfiable: picking one vertex per
  clause corresponds to choosing a true literal for that clause, and the
  contradiction edges guarantee a globally consistent assignment.

The implementation is straightforward and runs in polynomial time:
``O(C^2)`` where ``C`` is the number of clauses (the graph has ``3C``
vertices and at most ``3 * C * (C-1) / 2 + 3 * C`` edges).

The function ``reduce`` takes a 3‑SAT instance dictionary and returns an
Independent Set instance dictionary.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    Dict
        Independent‑Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    clauses: List[List[str]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Trivial cases handled by the construction automatically:
    # * If there are no clauses, k = 0 and the empty graph works.
    # * If there are clauses, each clause contributes exactly three vertices.
    vertex_id = 0
    # Mapping from vertex id to (var, is_positive)
    lit_of_vertex: List[Tuple[int, bool]] = []
    # For each clause, store the three vertex ids belonging to it.
    clause_vertices: List[List[int]] = []

    for clause in clauses:
        # clause is a list of three literals like "+1" or "-2"
        current: List[int] = []
        for lit in clause:
            sign = lit[0] == "+"
            var = int(lit[1:])  # variable numbers start at 1
            lit_of_vertex.append((var, sign))
            current.append(vertex_id)
            vertex_id += 1
        clause_vertices.append(current)

    n = vertex_id  # total vertices = 3 * num_clauses
    edges_set = set()

    # 1. Add edges inside each clause (make a triangle)
    for verts in clause_vertices:
        a, b, c = verts
        for u, v in ((a, b), (a, c), (b, c)):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # 2. Add contradiction edges between opposite literals of the same variable.
    # Build lists of vertices per variable per polarity.
    pos_vertices: Dict[int, List[int]] = {}
    neg_vertices: Dict[int, List[int]] = {}
    for vid, (var, sign) in enumerate(lit_of_vertex):
        if sign:
            pos_vertices.setdefault(var, []).append(vid)
        else:
            neg_vertices.setdefault(var, []).append(vid)

    for var in set(pos_vertices.keys()) | set(neg_vertices.keys()):
        pos_list = pos_vertices.get(var, [])
        neg_list = neg_vertices.get(var, [])
        for u in pos_list:
            for v in neg_list:
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in sorted(edges_set)]

    return {"n": n, "edges": edges, "k": num_clauses}

