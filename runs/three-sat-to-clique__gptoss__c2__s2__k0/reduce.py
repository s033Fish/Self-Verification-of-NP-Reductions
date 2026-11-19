"""Reduction from 3-SAT to Clique.

The source problem is defined by :class:`problems.ThreeSat` and the target
by :class:`problems.Clique`.  Both classes provide ``validate`` methods that
raise :class:`problems.InvalidInstance` when the instance does not follow the
specification.  The reduction must construct a Clique instance that has a
clique of size ``k`` **iff** the 3‑SAT formula is satisfiable.

Standard reduction:
    * For each clause create three vertices, one for each literal.
    * Connect two vertices belonging to *different* clauses unless the two
      literals are complementary (e.g. ``+x`` and ``-x``).  Vertices from the
      same clause are never connected.
    * Set ``k`` to the number of clauses.  A clique of size ``k`` picks exactly
      one literal from each clause, and the edge condition guarantees that the
      chosen literals are pairwise non‑contradictory – which is precisely a
      satisfying assignment.

Edge cases:
    * An empty formula (no clauses) is trivially satisfiable.  The Clique
      instance ``k = 0`` is always a yes‑instance, regardless of the graph.
    * The reduction works even if the same clause appears multiple times –
      each occurrence contributes its own three vertices.

The function runs in polynomial time with respect to the size of the 3‑SAT
instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem definitions for validation.  The import is safe because
# ``problems.py`` resides in the same directory.
from problems import ThreeSat, Clique, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary matching the format of :class:`problems.ThreeSat`.

    Returns
    -------
    dict
        An instance of the Clique problem satisfying the specification in
        ``problems.Clique``.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed, matching the contract of the reduction.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge‑case: empty formula.  Any graph with k = 0 is a yes‑instance.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal of each clause.
    # ``vertices`` holds tuples (clause_index, literal).
    vertices: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        # Each clause is guaranteed to have exactly three literals.
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)  # should be 3 * num_clauses
    edges: List[List[int]] = []

    # Add edges between vertices from different clauses unless the literals are
    # complementary (x and ¬x).  The graph is undirected, so we only add each
    # unordered pair once (a < b).
    for a in range(n):
        ci_a, lit_a = vertices[a]
        for b in range(a + 1, n):
            ci_b, lit_b = vertices[b]
            if ci_a == ci_b:
                # Vertices of the same clause must not be connected.
                continue
            if lit_a == -lit_b:
                # Complementary literals cannot coexist in a satisfying
                # assignment, so we omit the edge.
                continue
            edges.append([a, b])

    # The target instance must satisfy Clique's validation rules.
    target_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": num_clauses}
    Clique.validate(target_instance)
    return target_instance

