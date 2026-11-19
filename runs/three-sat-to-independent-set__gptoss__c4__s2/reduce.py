"""Reduction from 3‑SAT to Independent Set.

The source problem is :class:`ThreeSat` (3‑SAT) and the target problem is
``IndependentSet``.  The classic polynomial‑time reduction works as follows:

* For each clause create three vertices, one for each literal.
* Connect the three vertices of the same clause to form a triangle – an
  independent set can contain at most one vertex from each clause.
* For every variable connect every vertex that represents the positive literal
  with every vertex that represents the negative literal (across different
  clauses).  This prevents the independent set from picking both a literal and
  its complement.
* Set ``k`` (the required size of the independent set) to the number of
  clauses.  An independent set of size ``k`` corresponds to a truth assignment
  that satisfies every clause.

Edge cases:
    * If the formula contains **no clauses**, it is trivially satisfiable.
      We return a graph with ``n = 0`` vertices, no edges and ``k = 0`` – which
      is always a *yes* instance of Independent Set.

The implementation validates the input using the problem classes defined in
``problems.py`` and also validates the produced target instance before
returning it.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``IndependentSet`` format such that the
        answer to the returned instance is *yes* iff the answer to the input
        instance is *yes*.
    """

    # Validate source instance – will raise InvalidInstance on malformed input.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        result = {"n": 0, "edges": [], "k": 0}
        IndependentSet.validate(result)
        return result

    # Assign a unique vertex id to each literal occurrence.
    # Vertex id = clause_index * 3 + position_in_clause (0,1,2).
    n = num_clauses * 3
    edges: List[List[int]] = []

    # 1. Add triangle edges inside each clause.
    for i in range(num_clauses):
        v0 = i * 3
        v1 = i * 3 + 1
        v2 = i * 3 + 2
        edges.extend([[v0, v1], [v0, v2], [v1, v2]])

    # 2. Connect complementary literals across different clauses.
    # Build a mapping from (variable, sign) -> list of vertex ids.
    lit_to_vertices: Dict[tuple[int, bool], List[int]] = {}
    for i, clause in enumerate(clauses):
        for pos, literal in enumerate(clause):
            var = abs(literal)
            sign = literal > 0  # True for positive literal, False for negative.
            lit_to_vertices.setdefault((var, sign), []).append(i * 3 + pos)

    # For each variable, add edges between every positive vertex and every
    # negative vertex.
    for var in range(1, instance["num_vars"] + 1):
        pos_vertices = lit_to_vertices.get((var, True), [])
        neg_vertices = lit_to_vertices.get((var, False), [])
        for u in pos_vertices:
            for v in neg_vertices:
                edges.append([u, v])

    k = num_clauses
    result = {"n": n, "edges": edges, "k": k}
    IndependentSet.validate(result)
    return result

