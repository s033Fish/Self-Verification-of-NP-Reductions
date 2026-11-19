"""Reduction from SAT to Clique.

The source problem is SAT as defined in ``problems.Sat`` and the target
problem is Clique as defined in ``problems.Clique``.

For a CNF formula with *c* clauses we create a graph with one vertex for
every literal occurrence.  Vertices belonging to the same clause are never
connected.  Vertices belonging to different clauses are connected unless the
corresponding literals are contradictory, i.e. they refer to the same
variable with opposite signs.

It is well‑known that the formula is satisfiable iff the constructed graph has
a clique of size at least *c* (pick one true literal from each clause).

Edge cases are handled explicitly to keep the reduction total and
polynomial‑time:

* An empty list of clauses is always satisfiable – we output a graph with
  ``k = 0`` which is a yes‑instance for Clique.
* If any clause is empty the formula is unsatisfiable – we output a graph with
  ``k = 1`` but ``n = 0`` which is a no‑instance for Clique.

The implementation follows the specification of the instance formats in
``problems.py`` and does not call any solver.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique  # noqa: F401 – imported for type checking only


def _is_contradictory(lit1: int, lit2: int) -> bool:
    """Return ``True`` if ``lit1`` and ``lit2`` cannot both be true.

    Two literals are contradictory when they refer to the same variable with
    opposite signs, i.e. ``lit1 == -lit2``.
    """

    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT instance as described in the
        ``Sat`` class docstring.

    Returns
    -------
    dict
        A Clique instance ``{"n": int, "edges": List[List[int]], "k": int}``.
    """

    # Validate the SAT instance (will raise InvalidInstance on malformed input)
    Sat.validate(instance)  # type: ignore[arg-type]

    num_vars: int = instance["num_vars"]  # not directly used but kept for clarity
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Graph with 0 vertices and k=1 (k > n) is a definite NO.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses -> trivially satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices: each literal occurrence gets a unique vertex id.
    vertex_id = 0
    vertex_of: List[Tuple[int, int]] = []  # (clause_index, literal)
    clause_vertices: List[List[int]] = []  # mapping clause -> list of vertex ids
    for ci, clause in enumerate(clauses):
        ids_this_clause: List[int] = []
        for lit in clause:
            vertex_of.append((ci, lit))
            ids_this_clause.append(vertex_id)
            vertex_id += 1
        clause_vertices.append(ids_this_clause)

    n_vertices = vertex_id
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses unless contradictory.
    for i in range(len(clauses)):
        for j in range(i + 1, len(clauses)):
            for vi in clause_vertices[i]:
                lit_i = vertex_of[vi][1]
                for vj in clause_vertices[j]:
                    lit_j = vertex_of[vj][1]
                    if not _is_contradictory(lit_i, lit_j):
                        # Undirected edge – store with smaller endpoint first for consistency.
                        if vi < vj:
                            edges.append([vi, vj])
                        else:
                            edges.append([vj, vi])

    # k is the number of clauses.
    k = len(clauses)

    # The validation of the output will be performed by the caller/oracle.
    return {"n": n_vertices, "edges": edges, "k": k}

