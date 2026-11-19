"""Reduction from SAT to Clique.

The source problem is SAT as defined by the ``Sat`` class in ``problems.py``.
The target problem is Clique as defined by the ``Clique`` class.

For a CNF formula with ``c`` clauses we create a graph with a vertex for each
literal occurrence.  Vertices belonging to the same clause are never
connected.  Vertices from different clauses are connected unless the two
literals are complementary (e.g., ``x`` and ``¬x``).  A clique of size ``c``
corresponds exactly to a choice of one non‑conflicting literal from each
clause, i.e., a satisfying assignment.

Edge cases are handled automatically:
* If there are no clauses, ``c = 0`` and we output a graph with ``k = 0`` –
  the Clique problem is always yes for ``k <= 0``.
* If any clause is empty, there is no vertex representing that clause, so the
  maximum possible clique size is strictly less than ``c``; the Clique instance
  will correctly be a no‑instance.

The reduction runs in polynomial time in the size of the SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple

import problems  # The module containing Sat and Clique definitions


def reduce(instance: problems.Sat.Instance) -> problems.Clique.Instance:  # type: ignore[name-defined]
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` following the
        specification of ``Sat``.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": c}`` where ``c`` is
        the number of clauses.
    """
    # Validate the source instance (will raise if malformed).
    problems.Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)  # number of clauses → target clique size

    # Create a vertex for each literal occurrence.
    # Vertex IDs are 0..n-1 in the order they are added.
    vertices: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    edges: List[List[int]] = []

    # Add an undirected edge between vertices from different clauses unless
    # they are complementary literals of the same variable.
    for i in range(n):
        ci, lit_i = vertices[i]
        var_i = abs(lit_i)
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            if ci == cj:
                # Same clause – never connect.
                continue
            var_j = abs(lit_j)
            # Complementary literals conflict.
            if var_i == var_j and lit_i == -lit_j:
                continue
            edges.append([i, j])

    # Assemble the target instance.
    target_instance = {"n": n, "edges": edges, "k": c}
    # Validate the target instance to catch programming errors early.
    problems.Clique.validate(target_instance)
    return target_instance

