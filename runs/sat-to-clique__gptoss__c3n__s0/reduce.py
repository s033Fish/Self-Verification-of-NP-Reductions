"""Reduction from SAT (CNF) to Clique.

The source problem is :class:`Sat` defined in ``problems.py``.  An instance is a
dictionary ``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where literals
are non‑zero integers with sign indicating polarity.

The target problem is :class:`Clique`.  An instance is a dictionary
``{"n": n, "edges": [[u, v], ...], "k": k}``.

The classic polynomial‑time reduction creates one vertex for each literal in
each clause and connects vertices from different clauses unless the literals
are contradictory (i.e. they refer to the same variable with opposite signs).
The resulting graph has a clique of size equal to the number of clauses iff the
original formula is satisfiable.

Edge‑case handling follows the specification in ``problems.py``:

* An empty formula (no clauses) is trivially satisfiable – we return a graph
  with ``k = 0`` which is always a yes‑instance for Clique.
* If any clause is empty the formula is unsatisfiable – we return a graph where
  ``k`` is larger than the number of vertices, guaranteeing a no‑instance.

The function runs in time polynomial in the size of the SAT instance (linear
in the number of literals for vertex creation and quadratic for edge creation).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique


def _is_contradictory(lit1: int, lit2: int) -> bool:
    """Return ``True`` if ``lit1`` and ``lit2`` cannot both be true.

    The literals are contradictory exactly when they refer to the same
    variable with opposite signs, i.e. ``lit1 == -lit2``.
    """

    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary that satisfies :class:`Sat.validate`.

    Returns
    -------
    dict
        An instance that satisfies :class:`Clique.validate` and whose answer
        (yes/no) matches the answer for the SAT instance.
    """

    # Validate the input according to the source problem definition.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]  # not directly needed for the reduction
    clauses: List[List[int]] = instance["clauses"]

    # Edge case 1: formula contains an empty clause -> unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Return a graph where k > n, guaranteeing a NO answer.
        # n can be zero; using k = number_of_clauses + 1 works.
        return {"n": 0, "edges": [], "k": len(clauses) + 1}

    # Edge case 2: no clauses -> trivially satisfiable.
    if len(clauses) == 0:
        # Any graph with k <= 0 is a YES instance. Use the smallest possible.
        return {"n": 0, "edges": [], "k": 0}

    # Normal case: build the graph.
    # Assign a vertex index to each literal occurrence.
    vertex_of: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_of.append((ci, lit))

    n = len(vertex_of)
    edges: List[List[int]] = []

    # For every pair of vertices from different clauses, add an edge unless
    # the literals are contradictory.
    for i in range(n):
        ci, li = vertex_of[i]
        for j in range(i + 1, n):
            cj, lj = vertex_of[j]
            if ci == cj:
                # Vertices from the same clause are never connected.
                continue
            if _is_contradictory(li, lj):
                continue
            edges.append([i, j])

    k = len(clauses)
    # Validate the output according to the target problem definition.
    result = {"n": n, "edges": edges, "k": k}
    Clique.validate(result)
    return result

