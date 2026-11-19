"""Reduction from 3‑SAT to Independent Set.

The reduction follows the classic construction used in textbooks:

* For each clause `C_i` we create three vertices, one for each literal.
  These three vertices form a triangle (all three edges are present).
  Selecting an independent set of size `|C|` forces us to pick at most one
  vertex from each clause.

* For any two vertices that correspond to complementary literals
  (e.g. `x` and `¬x`) we add an edge between them.  This prevents the
  independent set from containing both a variable and its negation.

If the original formula is satisfiable, we can pick, for each clause, a
literal that is satisfied; the corresponding vertices form an independent
set of size `k = number_of_clauses`.  Conversely, any independent set of size
`k` yields a satisfying assignment by setting the selected literals to true.

The `reduce` function takes a validated 3‑SAT instance and returns a
validated Independent‑Set instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, IndependentSet


def _complement(lit: int) -> int:
    """Return the complementary literal of ``lit``.

    ``lit`` is a non‑zero integer where the sign denotes negation.
    """
    return -lit


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    The returned instance has the following fields:
        - ``n``: number of vertices (3 × #clauses)
        - ``edges``: list of undirected edges ``[u, v]`` with ``u < v``
        - ``k``: exactly the number of clauses
    """
    # Validate the source instance first – this also guarantees the format.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)
    # Mapping from (clause_index, literal_position) -> vertex id
    vertex_of: List[Tuple[int, int]] = []  # store (clause_idx, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_of.append((ci, lit))

    n = len(vertex_of)  # should be 3 * num_clauses
    edges_set = set()

    # 1. Add triangle edges inside each clause.
    for ci in range(num_clauses):
        base = ci * 3
        # vertices base, base+1, base+2 belong to this clause
        edges_set.add(frozenset((base, base + 1)))
        edges_set.add(frozenset((base, base + 2)))
        edges_set.add(frozenset((base + 1, base + 2)))

    # 2. Add edges between complementary literals across different clauses.
    # Build a map from literal to its vertex indices.
    lit_to_vertices: Dict[int, List[int]] = {}
    for v_id, (_, lit) in enumerate(vertex_of):
        lit_to_vertices.setdefault(lit, []).append(v_id)

    for lit, verts in lit_to_vertices.items():
        comp = _complement(lit)
        if comp not in lit_to_vertices:
            continue
        for v in verts:
            for u in lit_to_vertices[comp]:
                if v // 3 == u // 3:
                    # same clause – already connected via triangle; skip
                    continue
                # store edge with smaller id first to avoid duplicates
                a, b = (v, u) if v < u else (u, v)
                edges_set.add(frozenset((a, b)))

    # Convert edge set to required list format [[u, v], ...]
    edges: List[List[int]] = []
    for e in edges_set:
        u, v = sorted(list(e))
        edges.append([u, v])

    result = {"n": n, "edges": edges, "k": num_clauses}
    # Validate the target instance before returning.
    IndependentSet.validate(result)
    return result

