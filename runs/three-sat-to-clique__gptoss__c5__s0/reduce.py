"""Reduction from 3‑SAT to Clique.

The source problem is :class:`ThreeSat` and the target problem is
``Clique`` as defined in ``problems.py``.  The reduction follows the
standard textbook construction:

* For every clause ``C_i`` (there are ``c`` clauses) we create three
  vertices, one for each literal in the clause.  Vertex ``v`` therefore
  encodes a *pair* ``(i, literal)`` where ``i`` is the clause index and
  ``literal`` is the integer representation of the literal (positive for
  true, negative for false).
* Two vertices belonging to **different** clauses are connected by an
  edge iff the two literals are *compatible*, i.e. they are not the
  negation of each other.  Formally, vertices ``(i, ℓ)`` and ``(j, ℓ')``
  (with ``i != j``) receive an edge when ``abs(ℓ) != abs(ℓ')`` or
  ``ℓ == ℓ'``.
* The target asks for a clique of size ``k`` where ``k`` is the number of
  clauses.  A size‑``k`` clique can contain at most one vertex from each
  clause, and the compatibility condition guarantees that the selected
  literals can be simultaneously satisfied.

Edge cases:
    * If the formula has **no clauses**, it is trivially satisfiable.
      We output a Clique instance with ``k = 0`` (always a yes‑instance).
    * The construction works for any number of variables ``m`` – the
      reduction does not need to reference variables that never appear.

The function runs in polynomial time with respect to the size of the
input (``O(c^2)`` edges where ``c`` is the number of clauses).
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, Clique


def _compatible(lit_a: int, lit_b: int) -> bool:
    """Return ``True`` if the two literals can be true simultaneously.

    The literals are incompatible only when they refer to the same
    variable with opposite signs, i.e. ``lit_a == -lit_b``.
    """

    return not (abs(lit_a) == abs(lit_b) and lit_a == -lit_b)


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula, conforming to the
        format described in ``problems.py``.

    Returns
    -------
    Dict
        A dictionary representing a Clique instance.  The answer to the
        Clique instance is *yes* iff the original 3‑SAT formula is
        satisfiable.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.  Return a trivial
    # Clique instance with k = 0 (the specification guarantees a yes).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal in each clause.
    # vertex_id = clause_index * 3 + position_in_clause (0‑based).
    literals_by_vertex: List[int] = []  # index is vertex id, value is literal
    for clause in clauses:
        for lit in clause:
            literals_by_vertex.append(lit)

    n = len(literals_by_vertex)  # should be 3 * num_clauses
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses when compatible.
    for i in range(n):
        clause_i = i // 3
        lit_i = literals_by_vertex[i]
        for j in range(i + 1, n):
            clause_j = j // 3
            if clause_i == clause_j:
                # Vertices from the same clause must not be both chosen in a
                # clique of size num_clauses, so we omit edges within a clause.
                continue
            lit_j = literals_by_vertex[j]
            if _compatible(lit_i, lit_j):
                edges.append([i, j])

    # Build the target instance.
    target_instance: Dict = {"n": n, "edges": edges, "k": num_clauses}

    # Validate the produced instance (optional but helpful for debugging).
    Clique.validate(target_instance)
    return target_instance

