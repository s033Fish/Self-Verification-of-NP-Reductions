"""Reduction from 3‑SAT to Independent Set.

The reduction follows the classic construction:

* For each clause we create a triangle (3 vertices, one per literal).
  Edges inside the triangle enforce that an independent set can contain
  at most one vertex from each clause.
* For any two vertices whose literals are contradictory (they refer to the
  same variable with opposite signs) we add an edge. This prevents the
  independent set from selecting both, which would correspond to an
  inconsistent assignment.
* We ask for an independent set of size *k* where *k* equals the number of
  clauses. Selecting exactly one vertex from each triangle yields a
  satisfying assignment and vice‑versa.

The module provides a single function ``reduce(instance)`` that takes a
3‑SAT instance (as defined in ``problems.py``) and returns an Independent
Set instance.  The function validates the input using the problem class
validation helpers and runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Any

from problems import ThreeSat, IndependentSet


def _literal_vertex_map(clauses: List[List[int]]) -> List[Tuple[int, int]]:
    """Return a flat list mapping each vertex id to its literal.

    The vertex ids are assigned consecutively clause‑wise: the three
    vertices of clause ``i`` receive ids ``3*i, 3*i+1, 3*i+2``.
    """
    mapping: List[Tuple[int, int]] = []
    for clause in clauses:
        for lit in clause:
            mapping.append((len(mapping), lit))
    return mapping


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula, exactly as required by
        ``ThreeSat.validate``.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the format is wrong.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses → trivially satisfiable. Return a trivial
    # Independent Set instance where k=0 (always yes).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertex → literal mapping.
    vertex_literal: List[int] = []  # index is vertex id, value is literal
    for clause in clauses:
        for lit in clause:
            vertex_literal.append(lit)

    n = len(vertex_literal)  # should be 3 * num_clauses
    edges: List[List[int]] = []

    # 1. Add edges inside each clause (forming a triangle).
    for i in range(num_clauses):
        base = 3 * i
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    # 2. Add edges between contradictory literals from different clauses.
    # Two literals are contradictory if they refer to the same variable with
    # opposite signs, i.e., lit1 == -lit2.
    for u in range(n):
        lit_u = vertex_literal[u]
        for v in range(u + 1, n):
            # Skip pairs that are already connected inside the same clause;
            # those edges are already present, but adding a duplicate would
            # violate the validation rules, so we explicitly avoid them.
            if u // 3 == v // 3:
                continue
            lit_v = vertex_literal[v]
            if lit_u == -lit_v:
                edges.append([u, v])

    # The target instance must satisfy IndependentSet.validate, which checks
    # that edges are unique and vertices are within range. The construction
    # above guarantees that.
    target_instance = {"n": n, "edges": edges, "k": num_clauses}
    IndependentSet.validate(target_instance)
    return target_instance

