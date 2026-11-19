"""Reduction from SAT to Clique.

The source problem is SAT (CNF satisfiability) as defined in ``problems.py``
under the ``Sat`` class.  The target problem is Clique as defined by the
``Clique`` class.

For a SAT instance with ``m`` variables and ``c`` clauses we construct a
graph ``G`` with a vertex for every literal that appears in a clause.  Vertices
belonging to the same clause are never connected.  Vertices belonging to two
different clauses are connected **iff** the corresponding literals are not
directly contradictory (i.e. they are not ``v`` and ``-v`` for the same
variable ``v``).  The target parameter ``k`` is set to the number of clauses.

Standard folklore argument:

*If the SAT formula is satisfiable*, choose a true literal from each clause.
The chosen vertices are pairwise compatible, so they form a clique of size
``c``.

*If the SAT formula is unsatisfiable*, any selection of at most one literal per
clause cannot satisfy all clauses, which means at least one pair of chosen
vertices will be contradictory or a clause is empty (providing no vertex).
Consequently the graph contains no clique of size ``c``.

Edge‑case handling:
  * ``c == 0`` – an empty formula is always satisfiable.  We output a graph
    with ``n = 0`` vertices, no edges, and ``k = 0``.  By the Clique definition
    ``k <= 0`` is always a yes‑instance.
  * An empty clause yields zero vertices for that clause.  Because ``k`` is
    still the total number of clauses, any clique can contain at most
    ``c-1`` vertices, correctly reflecting unsatisfiability.

The implementation below follows the description and validates both the input
and the produced output using the classes from ``problems.py``.
"""

from __future__ import annotations

from typing import List, Tuple, Dict

from problems import Sat, Clique, InvalidInstance


def _compatible(lit1: int, lit2: int) -> bool:
    """Return ``True`` if the two literals do not contradict each other.

    Two literals contradict each other exactly when they refer to the same
    variable with opposite signs, i.e. ``lit1 == -lit2``.
    """

    return lit1 != -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Clique`` format such that the SAT
        instance is a yes‑instance iff the produced Clique instance is a
        yes‑instance.
    """

    # Validate the SAT instance first – this will raise ``InvalidInstance``
    # if the input does not conform to the specification.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses: int = len(clauses)

    # Edge case: no clauses → always satisfiable.  We can output any graph with
    # k <= 0.  The smallest possible graph is the empty graph.
    if num_clauses == 0:
        result = {"n": 0, "edges": [], "k": 0}
        Clique.validate(result)
        return result

    # Build vertices: each literal in each clause becomes a vertex.
    # We assign a consecutive integer id to each vertex.
    vertex_info: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n = len(vertex_info)
    # Construct edges between vertices belonging to different clauses and that
    # are compatible.
    edges: List[List[int]] = []
    for i in range(n):
        ci, lit_i = vertex_info[i]
        for j in range(i + 1, n):
            cj, lit_j = vertex_info[j]
            if ci == cj:
                # Same clause – never connect.
                continue
            if _compatible(lit_i, lit_j):
                edges.append([i, j])

    result = {"n": n, "edges": edges, "k": num_clauses}
    # Validate the produced Clique instance.
    Clique.validate(result)
    return result

