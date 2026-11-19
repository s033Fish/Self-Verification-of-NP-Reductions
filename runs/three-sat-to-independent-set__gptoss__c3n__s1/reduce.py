"""Reduction from 3‑SAT to Independent Set.

The reduction follows the classic textbook construction:

* For each clause create a triangle (3‑clique) – the three vertices
  represent the three literals of the clause. Selecting at most one
  vertex from each triangle guarantees that at most one literal per
  clause is chosen.
* Add an edge between any two vertices whose literals are contradictory
  (i.e., one is ``x`` and the other is ``-x``).  This prevents a selection
  that would assign both a variable and its negation to ``True``.

An independent set of size ``C`` (the number of clauses) therefore picks
exactly one literal from each clause, and none of the chosen literals are
pairwise contradictory – which is precisely a satisfying assignment.

The ``reduce`` function validates the source instance using the provided
``ThreeSat.validate`` method and returns a dictionary that conforms to the
``IndependentSet`` format.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as described in
        ``ThreeSat``'s docstring.

    Returns
    -------
    dict
        An ``IndependentSet`` instance ``{"n": n, "edges": [...], "k": k}``
        where ``k`` equals the number of clauses.
    """

    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    C = len(clauses)  # number of clauses

    # Each clause contributes three vertices.
    n = 3 * C
    edges: List[List[int]] = []

    # Helper to map (clause_index, literal_position) -> vertex id
    def vertex_id(ci: int, pos: int) -> int:
        return ci * 3 + pos

    # 1. Add edges to make each clause a triangle (K3).
    for ci, clause in enumerate(clauses):
        v0 = vertex_id(ci, 0)
        v1 = vertex_id(ci, 1)
        v2 = vertex_id(ci, 2)
        edges.append([v0, v1])
        edges.append([v0, v2])
        edges.append([v1, v2])

    # 2. Add edges between contradictory literals across different clauses.
    # Build a list of (vertex, var, sign) for all vertices.
    literals_info = []  # (vertex, var, sign)
    for ci, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            literals_info.append((vertex_id(ci, pos), var, sign))

    # Compare each pair from different clauses.
    total = len(literals_info)
    for i in range(total):
        vi, var_i, sign_i = literals_info[i]
        for j in range(i + 1, total):
            vj, var_j, sign_j = literals_info[j]
            # Skip pairs from the same clause – already connected via triangle.
            if vi // 3 == vj // 3:
                continue
            if var_i == var_j and sign_i != sign_j:
                edges.append([vi, vj])

    # The target instance expects k = number of clauses (size of independent set).
    k = C

    target_instance = {"n": n, "edges": edges, "k": k}
    # Validate the constructed target instance.
    IndependentSet.validate(target_instance)
    return target_instance

