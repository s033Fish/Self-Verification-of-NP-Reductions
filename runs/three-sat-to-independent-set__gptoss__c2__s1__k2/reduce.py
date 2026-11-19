"""Reduction from 3‑SAT to Independent Set.

The source problem (ThreeSat) uses instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable ``v`` is true)
or ``-v`` (meaning variable ``v`` is false).  Every clause contains exactly three
different variables.

The target problem (IndependentSet) expects a graph described by the number of
vertices ``n``, a list of undirected edges ``[[u, v], ...]`` and a parameter
``k``.  The answer is *yes* iff the graph contains an independent set of size at
least ``k``.

Standard textbook reduction:

* For each clause create a triangle (three vertices, all pairwise adjacent).
  This forces any independent set to contain **at most** one vertex from each
  clause.
* Connect vertices whose literals are complementary (``v`` and ``-v``) across
  different clauses.  This guarantees that an independent set cannot contain a
  literal and its negation simultaneously, which would correspond to an
  inconsistent assignment.
* Set ``k`` to the number of clauses.  An independent set of size ``k`` must pick
  exactly one vertex from each clause, and the chosen literals form a satisfying
  assignment.

Edge‑case handling:
    * If the formula has **no clauses** it is trivially satisfiable.  We output
      an empty graph (``n = 0``) with ``k = 0`` – the Independent Set problem
      defines ``k <= 0`` as always a *yes* instance.

The implementation below follows this construction.  It runs in time O(C^2)
where ``C`` is the number of clauses, which is polynomial in the input size.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary following the ``ThreeSat`` specification.

    Returns
    -------
    dict
        An ``IndependentSet`` instance ``{"n": n, "edges": edges, "k": k}``.
    """

    # Extract data from the 3‑SAT instance.
    num_vars = instance.get("num_vars")  # not directly needed for the reduction
    clauses: List[List[int]] = instance.get("clauses", [])

    # Number of clauses determines the required independent‑set size.
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # vertex_id[clause_index][position] gives the global vertex number.
    vertex_id: List[List[int]] = []
    for i in range(num_clauses):
        base = i * 3
        vertex_id.append([base, base + 1, base + 2])

    n_vertices = 3 * num_clauses
    edges: List[List[int]] = []
    seen_edges = set()  # to avoid duplicates; store frozenset({u, v})

    # Helper to add an undirected edge exactly once.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        key = frozenset((u, v))
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append([u, v])

    # 1. Connect vertices within each clause to form a triangle.
    for i in range(num_clauses):
        ids = vertex_id[i]
        add_edge(ids[0], ids[1])
        add_edge(ids[0], ids[2])
        add_edge(ids[1], ids[2])

    # 2. Connect complementary literals across different clauses.
    # Build a mapping from literal value to the list of (clause, position, vertex).
    literal_map: Dict[int, List[tuple[int, int, int]]] = {}
    for ci, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            literal_map.setdefault(lit, []).append((ci, pos, vertex_id[ci][pos]))

    # For each literal, connect its occurrences to occurrences of its negation.
    for lit, occs in literal_map.items():
        neg = -lit
        if neg not in literal_map:
            continue
        for (_, _, v1) in occs:
            for (_, _, v2) in literal_map[neg]:
                # Only add edges between different clauses (the same clause
                # already has a triangle edge, and literals in the same clause
                # cannot be complementary by problem definition).
                if v1 != v2:
                    add_edge(v1, v2)

    # The required independent set size is the number of clauses.
    k = num_clauses

    return {"n": n_vertices, "edges": edges, "k": k}

