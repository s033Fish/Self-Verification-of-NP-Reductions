"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined by :class:`Sat` in ``problems.py`` and the
target problem by :class:`Clique`.  Both classes only provide a ``validate``
method – there are no solvers.  This file implements ``reduce`` which takes a
SAT instance and returns a Clique instance such that the SAT instance is
satisfiable *iff* the produced graph contains a clique of size at least ``k``.

The classic polynomial‑time reduction works as follows:

* For each literal occurrence in each clause we create a vertex.
* Vertices belonging to the same clause are never connected – a clique must
  pick at most one literal from each clause.
* Vertices from different clauses are connected unless the two literals are
  contradictory, i.e. they refer to the same variable with opposite signs.
* The required clique size ``k`` is the number of clauses.

Edge Cases
~~~~~~~~~~
* **No clauses** – the formula is vacuously satisfiable.  We return a graph
  with ``k = 0`` (always a yes instance for Clique).
* **An empty clause** – such a formula is unsatisfiable.  In the reduction the
  empty clause contributes no vertices, therefore a clique of size ``k``
  cannot exist, correctly yielding a no‑instance.

The implementation follows the description above and respects the validation
rules of both problems.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List

from problems import Sat, Clique


def _validate_sat(instance: Dict) -> None:
    """Validate the SAT instance using the class method.

    ``Sat.validate`` raises ``InvalidInstance`` on malformed input – we simply
    forward that exception.
    """

    Sat.validate(instance)


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format required by :class:`Sat`.

    Returns
    -------
    dict
        A Clique instance (``{"n": ..., "edges": ..., "k": ...}``).
    """

    # Validate the source instance first.
    _validate_sat(instance)

    # Extract data.
    num_vars = instance["num_vars"]  # not used directly but kept for clarity
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)  # number of clauses, also the required clique size

    # Edge case: no clauses → trivially satisfiable.  Clique with k=0 is always yes.
    if c == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices: each literal occurrence gets its own vertex.
    # vertex_info maps vertex id -> (clause_index, literal).
    vertex_info: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n_vertices = len(vertex_info)

    # Helper to decide if two literals are compatible (i.e., not contradictory).
    def compatible(lit1: int, lit2: int) -> bool:
        # Contradiction occurs when they refer to the same variable with opposite signs.
        return not (abs(lit1) == abs(lit2) and lit1 != lit2)

    edges: List[List[int]] = []
    # Add edges between vertices from different clauses if compatible.
    for (u, (ci_u, lit_u)), (v, (ci_v, lit_v)) in combinations(enumerate(vertex_info), 2):
        if ci_u == ci_v:
            # Same clause – never connect.
            continue
        if compatible(lit_u, lit_v):
            # Store edge with smaller vertex first to satisfy validation.
            edges.append([u, v] if u < v else [v, u])

    # Construct the target instance.
    target_instance = {"n": n_vertices, "edges": edges, "k": c}
    # Validate the produced Clique instance (will raise if something is wrong).
    Clique.validate(target_instance)
    return target_instance

