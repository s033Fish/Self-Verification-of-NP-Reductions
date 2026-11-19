"""Reduction from SAT to Clique.

The source problem is SAT (CNF satisfiability) as defined in ``problems.py``.
The target problem is Clique.

Standard polynomial‑time reduction:
    * For each clause i and each literal ℓ in that clause create a vertex
      labelled (i, ℓ).
    * Connect two vertices belonging to different clauses unless the two
      literals are contradictory, i.e. they refer to the same variable with
      opposite signs.
    * Set ``k`` to the number of clauses.

With this construction a k‑clique corresponds exactly to a choice of one
literal from each clause that are pairwise non‑contradictory, which yields a
truth assignment satisfying the formula.  The construction also respects the
edge cases described in the problem statements:
    * If the formula has no clauses, ``k = 0`` and the Clique instance is a
      trivial yes‑instance because any graph has a clique of size ≥ 0.
    * If a clause is empty, the clause contributes no vertices, so a clique
      of size ``k`` cannot exist – the reduction correctly maps the formula
      to a no‑instance.

The function ``reduce`` validates the input SAT instance, builds the graph as
described, and returns a dictionary suitable for the Clique problem.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique


def _is_contradictory(lit1: int, lit2: int) -> bool:
    """Return True iff ``lit1`` and ``lit2`` cannot both be true.

    Two literals contradict each other exactly when they refer to the same
    variable with opposite signs, i.e. ``abs(lit1) == abs(lit2)`` and the
    literals differ.
    """

    return abs(lit1) == abs(lit2) and lit1 != lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT instance as described in
        ``problems.Sat``.

    Returns
    -------
    dict
        A dictionary representing a Clique instance.  The keys are ``n``,
        ``edges`` and ``k``.
    """

    # Validate the SAT instance – this will raise InvalidInstance on malformed
    # input, matching the behaviour expected by the task harness.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Mapping from (clause_index, literal) to vertex id
    vertex_id: Dict[Tuple[int, int], int] = {}
    vertices: List[Tuple[int, int]] = []  # list of (clause_index, literal)
    next_id = 0
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_id[(ci, lit)] = next_id
            vertices.append((ci, lit))
            next_id += 1

    n = next_id  # total number of vertices
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses that are not contradictory
    for i in range(len(vertices)):
        ci, lit_i = vertices[i]
        for j in range(i + 1, len(vertices)):
            cj, lit_j = vertices[j]
            if ci == cj:
                # vertices from the same clause must not be connected – we need
                # exactly one vertex per clause in a clique.
                continue
            if _is_contradictory(lit_i, lit_j):
                continue
            edges.append([i, j])

    # The required clique size is the number of clauses.
    k = num_clauses

    # Build the Clique instance dictionary.
    clique_instance: Dict = {"n": n, "edges": edges, "k": k}

    # Validate the produced instance to catch programming mistakes early.
    Clique.validate(clique_instance)
    return clique_instance

