"""Reduction from 3‑SAT to Clique.

The source problem is defined by :class:`ThreeSat` (see ``problems.py``).
The target problem is :class:`Clique`.  Both classes provide ``validate``
and ``is_yes`` methods that we can use to ensure our reduction produces a
well‑formed instance and that the answer is preserved.

Classic reduction:
    * Create a vertex for each literal in each clause (three vertices per
      clause because every clause has exactly three literals).
    * Connect two vertices with an edge iff they belong to *different*
      clauses **and** the two literals are not contradictory – i.e. they do
      not refer to the same variable with opposite polarity.
    * Set the required clique size ``k`` to the number of clauses.

If the formula has no clauses, it is trivially satisfiable.  The Clique
instance ``k = 0`` is always a yes‑instance, so we return an empty graph.

The implementation follows the specification literally and runs in
polynomial time (quadratic in the number of vertices, which is ``3·|C|``).
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, Clique


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an equivalent Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as defined by
        ``ThreeSat`` – it must contain the keys ``"num_vars"`` and
        ``"clauses"``.

    Returns
    -------
    dict
        A Clique instance (keys ``"n"``, ``"edges"``, ``"k"``) such that the
        Clique answer is *yes* iff the original formula is satisfiable.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input does not follow the spec.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.  Clique with k <= 0 is
    # always a yes‑instance, so we can safely return an empty graph.
    if num_clauses == 0:
        result = {"n": 0, "edges": [], "k": 0}
        Clique.validate(result)
        return result

    # Build a list of literals, one per vertex, and remember which clause a
    # vertex belongs to.
    literals: List[int] = []
    clause_of_vertex: List[int] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            literals.append(lit)
            clause_of_vertex.append(ci)

    n = len(literals)  # should be 3 * num_clauses
    edges: List[List[int]] = []

    # Add edges between compatible vertices from different clauses.
    for i in range(n):
        for j in range(i + 1, n):
            if clause_of_vertex[i] == clause_of_vertex[j]:
                # Vertices from the same clause must not be chosen together.
                continue
            li = literals[i]
            lj = literals[j]
            # Contradiction occurs when the same variable appears with opposite
            # signs.  In that case the two vertices cannot coexist in a clique.
            if abs(li) == abs(lj) and li != lj:
                continue
            edges.append([i, j])

    k = num_clauses
    result = {"n": n, "edges": edges, "k": k}
    # Ensure the produced instance conforms to the Clique specification.
    Clique.validate(result)
    return result

