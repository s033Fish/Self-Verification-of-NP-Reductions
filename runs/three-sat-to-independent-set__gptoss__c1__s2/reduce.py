"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains exactly three
distinct variables.

The target problem is ``IndependentSet`` with an instance format ::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 .. n-1`` and edges are undirected pairs with ``u !=
v``.  An independent set of size at least ``k`` must contain no edge between any
two of its vertices.

The classic polynomial‑time reduction works as follows:

* For each clause we create a triangle (three vertices, fully connected).  The
  triangle forces that at most one vertex from the clause can be chosen in an
  independent set.
* Vertices representing complementary literals (e.g. ``+x`` and ``-x``) are
  connected across clauses.  This guarantees that an independent set cannot pick
  both a literal and its negation.
* We ask for an independent set of size equal to the number of clauses ``C``.
  Selecting exactly one vertex from each triangle corresponds to picking a
  literal that satisfies the clause, and the cross‑clause edges enforce that
  the selected literals are globally consistent – i.e. they define a satisfying
  assignment.

The reduction runs in polynomial time: the graph has ``3*C`` vertices and at
most ``3*C choose 2`` edges, which is ``O(C^2)``.

The ``reduce`` function below implements this transformation.  It does **not**
rely on any solver; it simply constructs the graph and returns the target
instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of literals).  Literals are represented as signed
        integers, e.g. ``+3`` is ``3`` and ``-2`` is ``-2``.

    Returns
    -------
    Dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Number of vertices: three per clause.
    n = num_clauses * 3
    k = num_clauses  # we need one vertex per clause

    # Helper to map (clause_index, position_in_clause) -> vertex id
    def vertex_id(ci: int, pos: int) -> int:
        return ci * 3 + pos

    edges_set: Set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause to form a triangle.
    for ci, clause in enumerate(clauses):
        # clause has exactly three literals; we still guard against malformed.
        for a in range(3):
            for b in range(a + 1, 3):
                u = vertex_id(ci, a)
                v = vertex_id(ci, b)
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals across different clauses.
    # Build a map from literal value to list of (clause_index, position).
    literal_map: Dict[int, List[Tuple[int, int]]] = {}
    for ci, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            literal_map.setdefault(lit, []).append((ci, pos))

    # For each variable, connect +v vertices to -v vertices.
    # Determine the set of variables present.
    vars_seen: Set[int] = set()
    for lit in literal_map:
        vars_seen.add(abs(lit))
    for var in vars_seen:
        pos_vertices = literal_map.get(var, [])
        neg_vertices = literal_map.get(-var, [])
        for (ci1, p1) in pos_vertices:
            for (ci2, p2) in neg_vertices:
                # Avoid self‑edge (should not happen because a clause never
                # contains both v and -v by definition).
                u = vertex_id(ci1, p1)
                v = vertex_id(ci2, p2)
                if u == v:
                    continue
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # Convert edge set to required list format.
    edges: List[List[int]] = [[u, v] for (u, v) in sorted(edges_set)]

    return {"n": n, "edges": edges, "k": k}

