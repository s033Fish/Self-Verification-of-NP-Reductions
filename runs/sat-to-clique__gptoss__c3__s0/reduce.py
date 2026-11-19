"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined by the :class:`Sat` class in ``problems.py``.
An instance is a dictionary ``{"num_vars": m, "clauses": [[lit, ...], ...]}``
where each literal is an integer ``+v`` (variable *v* true) or ``-v`` (variable
*v* false).  The target problem is the :class:`Clique` class, whose instance
format is ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The classic polynomial‑time reduction creates one vertex for every literal in
every clause.  Vertices belonging to the same clause are never connected.  Two
vertices from different clauses are connected iff the corresponding literals
are **not** contradictory, i.e. they are not of the form ``v`` and ``-v`` for the
same variable *v*.  The reduction asks for a clique of size ``k`` equal to the
number of clauses.  Selecting one vertex per clause yields a satisfying
assignment exactly when those vertices form a clique.

Edge‑case handling mirrors the specifications in ``problems.py``:

* If the formula contains **no clauses**, ``k = 0`` and the graph has ``n = 0``
  vertices – a trivially yes instance because ``k <= 0`` is always yes.
* An **empty clause** contributes no vertices, making it impossible to obtain a
  clique of size ``k`` (which equals the total number of clauses).  Hence the
  reduced instance is a no‑instance, matching the unsatisfiable source.
* Tautological clauses (containing both *v* and ``-v``) are handled naturally;
  the reduction still provides a vertex for each literal, and the freedom to
  pick either literal ensures a clique can be formed whenever the whole
  formula is satisfiable.

The implementation below follows this construction and runs in polynomial time
with respect to the size of the input formula.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique


def _contradictory(lit1: int, lit2: int) -> bool:
    """Return ``True`` if the two literals cannot both be true.

    The literals are contradictory exactly when they refer to the same variable
    with opposite signs, i.e. ``v`` and ``-v``.
    """

    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary following the SAT specification.

    Returns
    -------
    dict
        A dictionary following the Clique specification such that the answer
        to the Clique instance is *yes* iff the answer to the SAT instance is
        *yes*.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.  The reduction itself does not need to handle malformed
    # inputs.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Assign a vertex index to each literal in each clause.
    # Mapping: (clause_index, literal_position) -> vertex_id
    vertex_id = 0
    clause_vertices: List[List[Tuple[int, int]]] = []  # list per clause of (literal, vertex_id)
    for ci, clause in enumerate(clauses):
        cur: List[Tuple[int, int]] = []
        for lit in clause:
            cur.append((lit, vertex_id))
            vertex_id += 1
        clause_vertices.append(cur)

    n = vertex_id  # total number of vertices
    edges: List[List[int]] = []

    # Add edges between vertices from different clauses when literals are not
    # contradictory.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for lit_i, v_i in clause_vertices[i]:
                for lit_j, v_j in clause_vertices[j]:
                    if not _contradictory(lit_i, lit_j):
                        edges.append([v_i, v_j])

    # Build the target instance.  The required clique size is the number of
    # clauses.
    target_instance = {"n": n, "edges": edges, "k": num_clauses}

    # Validate the produced instance to catch programming errors early.
    Clique.validate(target_instance)
    return target_instance

