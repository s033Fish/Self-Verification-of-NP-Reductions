"""Reduction from SAT (CNF) to Clique.

The reduction follows the classic textbook construction:

* For each clause C_i and each literal ℓ in C_i we create a vertex v_{i,ℓ}.
* We set the target clique size k to the number of clauses.
* We add an edge between two vertices belonging to *different* clauses
  unless the corresponding literals are contradictory, i.e. they refer to
  the same variable with opposite signs (v and ¬v).

The resulting graph has a clique of size k iff the original formula is
 satisfiable – a clique selects exactly one literal from each clause and the
 selected literals are mutually compatible, which yields a satisfying
 assignment.

Edge‑case handling:
  - If the formula has **no clauses** it is trivially satisfiable.  We
    return a graph with k = 0 (always a yes‑instance of Clique).
  - If any clause is empty the formula is unsatisfiable.  We return a
    graph with n = 0 and k = 1, which is a no‑instance because k > n.

The implementation validates the input using the provided problem classes
 and validates the constructed output before returning it.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Sat, Clique


def _contradictory(lit1: int, lit2: int) -> bool:
    """Return True if ``lit1`` and ``lit2`` cannot both be true.

    The literals are encoded as signed integers where the absolute value is the
    variable index and the sign indicates polarity.  Two literals are
    contradictory exactly when they refer to the same variable with opposite
    signs.
    """

    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to ``Sat``'s format.

    Returns
    -------
    Dict
        A dictionary adhering to ``Clique``'s format.
    """

    # Validate the source instance first – this will raise InvalidInstance on
    # malformed input.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]  # not directly needed for reduction
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: formula with no clauses is always satisfiable.
    if len(clauses) == 0:
        # k = 0 guarantees a yes‑instance for Clique.
        result = {"n": 0, "edges": [], "k": 0}
        Clique.validate(result)
        return result

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        # Produce a graph with n = 0 and k = 1 (k > n) => always no.
        result = {"n": 0, "edges": [], "k": 1}
        Clique.validate(result)
        return result

    # Normal case – build vertices.
    # Assign a unique integer id to each (clause_index, literal_position).
    vertex_id: List[List[int]] = []  # vertex_id[i][j] gives id for clause i, literal j
    literals: List[int] = []  # flatten list of literals indexed by vertex id
    current_id = 0
    for clause in clauses:
        ids_for_clause: List[int] = []
        for lit in clause:
            ids_for_clause.append(current_id)
            literals.append(lit)
            current_id += 1
        vertex_id.append(ids_for_clause)

    n_vertices = current_id
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses when literals are not
    # contradictory.
    num_clauses = len(clauses)
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for vi in vertex_id[i]:
                lit_i = literals[vi]
                for vj in vertex_id[j]:
                    lit_j = literals[vj]
                    if not _contradictory(lit_i, lit_j):
                        edges.append([vi, vj])

    result = {"n": n_vertices, "edges": edges, "k": num_clauses}
    # Validate the constructed target instance.
    Clique.validate(result)
    return result

