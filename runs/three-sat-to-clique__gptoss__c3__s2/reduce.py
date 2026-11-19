"""Reduction from 3-SAT (SOURCE) to Clique (TARGET).

The reduction follows the classic textbook construction:

* For each clause of the 3‑SAT formula we create three vertices, one for each
  literal appearing in the clause.
* Vertices belonging to the same clause are never connected.
* Vertices from different clauses are connected **iff** the corresponding
  literals are not complementary (i.e., we do not have ``x`` in one vertex and
  ``¬x`` in the other).
* The target instance asks for a clique of size equal to the number of
  clauses. Such a clique exists exactly when the original formula is
  satisfiable.

Edge cases:
    - An empty formula (no clauses) is always satisfiable. We map it to a
      Clique instance with ``k = 0`` (always a yes‑instance) and an empty graph.
    - The construction works for any number of clauses ≥ 1.

The function runs in time polynomial in the size of the 3‑SAT instance –
specifically O(c²) where ``c`` is the number of clauses.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem definitions to reuse validation helpers.
from problems import ThreeSat, Clique


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A valid 3‑SAT instance as defined by :class:`ThreeSat`.

    Returns
    -------
    dict
        A Clique instance. The answer to the returned instance is *yes* iff
        the answer to the input instance is *yes*.
    """
    # Ensure the source instance conforms to the specification.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        # An empty graph with k = 0 satisfies the Clique yes‑condition.
        return {"n": 0, "edges": [], "k": 0}

    # Create a list of literals for each vertex. Vertex ids are assigned in the
    # order (clause 0 literal 0), (clause 0 literal 1), (clause 0 literal 2),
    # (clause 1 literal 0), ...
    literals: List[int] = []
    for clause in clauses:
        # Each clause is guaranteed to have exactly three literals by the
        # validator.
        literals.extend(clause)

    n = num_clauses * 3  # total vertices
    edges: List[List[int]] = []

    # Add edges between vertices from different clauses when the literals are
    # not contradictory.
    for i in range(num_clauses):
        for j in range(3):
            v1 = i * 3 + j
            lit1 = literals[v1]
            for i2 in range(i + 1, num_clauses):
                for j2 in range(3):
                    v2 = i2 * 3 + j2
                    lit2 = literals[v2]
                    # Do not connect complementary literals.
                    if lit1 != -lit2:
                        edges.append([v1, v2])

    # The target asks for a clique of size equal to the number of clauses.
    k = num_clauses

    # Validate the constructed target instance before returning (helps catch
    # programming errors during development).
    target_instance = {"n": n, "edges": edges, "k": k}
    Clique.validate(target_instance)
    return target_instance

