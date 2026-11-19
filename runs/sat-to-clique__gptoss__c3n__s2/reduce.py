"""Reduction from SAT (CNF) to Clique.

The reduction follows the classic textbook construction:

* For each clause *C_i* in the SAT instance we create a vertex for every
  literal that appears in *C_i* (including duplicate literals – each
  occurrence becomes its own vertex).
* Two vertices from *different* clauses are connected by an edge iff the
  corresponding literals are **not** contradictory, i.e. they are not of the
  form *x* and *¬x*.
* The target graph asks for a clique of size *k* where *k* equals the number
  of clauses.  A size‑*k* clique corresponds exactly to picking one literal
  from each clause that are mutually non‑contradictory, which is precisely a
  satisfying assignment.

Edge‑case handling:
  - If the formula has **no clauses**, SAT is trivially satisfiable.  We
    return a Clique instance with ``k = 0`` (always a YES instance).
  - If the formula contains an **empty clause** ``[]`` it is unsatisfiable.
    We return a Clique instance with ``n = 0`` and ``k = 1`` – the condition
    ``k > n`` is a guaranteed NO.

The implementation validates both the input and the produced output using
the validation helpers defined in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import Sat, Clique, InvalidInstance


def _build_graph(clauses: List[List[int]]) -> Tuple[int, List[List[int]]]:
    """Construct the graph for the standard reduction.

    Returns a tuple ``(n, edges)`` where ``n`` is the number of vertices and
    ``edges`` is a list of ``[u, v]`` pairs.
    """
    # Assign a vertex id to each literal occurrence.
    vertex_info: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n = len(vertex_info)
    edges: List[List[int]] = []
    # Compare every pair of vertices from different clauses.
    for u in range(n):
        ci_u, lit_u = vertex_info[u]
        for v in range(u + 1, n):
            ci_v, lit_v = vertex_info[v]
            if ci_u == ci_v:
                continue  # same clause – never an edge
            # No edge if literals are contradictory (x and -x).
            if lit_u == -lit_v:
                continue
            edges.append([u, v])
    return n, edges


def reduce(instance: object) -> dict:
    """Reduce a SAT instance to a Clique instance.

    The returned dictionary follows the format required by ``Clique``:
    ``{"n": n, "edges": edges, "k": k}``.
    """
    # Validate the SAT instance first.
    Sat.validate(instance)
    assert isinstance(instance, dict)
    # num_vars is not directly needed for reduction but we keep it for clarity.
    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: formula contains an empty clause -> unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        # Produce a graph where k > n, which is always a NO instance.
        result = {"n": 0, "edges": [], "k": 1}
        Clique.validate(result)
        return result

    # Edge case: no clauses -> trivially satisfiable.
    if len(clauses) == 0:
        result = {"n": 0, "edges": [], "k": 0}
        Clique.validate(result)
        return result

    # General case.
    n, edges = _build_graph(clauses)
    k = len(clauses)
    result = {"n": n, "edges": edges, "k": k}
    # Validate the constructed Clique instance.
    Clique.validate(result)
    return result

