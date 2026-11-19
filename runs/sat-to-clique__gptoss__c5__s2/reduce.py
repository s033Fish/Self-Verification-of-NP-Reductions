"""Reduction from SAT (CNF) to Clique.

The classic polynomial‑time reduction creates a vertex for every literal
occurring in a clause. Two vertices are connected by an edge iff they belong
to *different* clauses and the corresponding literals are not contradictory
(`x` vs `¬x`). A k‑clique (where k = number of clauses) therefore selects
exactly one literal from each clause that are pairwise compatible – this is
exactly a satisfying assignment.

Edge‑case handling matches the specifications in ``problems.py``:

* If the formula has **no clauses**, it is trivially satisfiable.  We return a
  graph with ``k = 0`` (always a yes‑instance because k ≤ 0 is always yes).
* If any clause is **empty**, the formula is unsatisfiable.  We return a graph
  with ``n = 0`` and ``k = 1`` – since ``k > n`` this is always a no‑instance.

The function ``reduce`` validates the input using ``Sat.validate`` and returns
an instance that satisfies ``Clique.validate``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique


def _literal_key(literal: int) -> Tuple[int, bool]:
    """Return a canonical representation of a literal.

    ``literal`` is an int where sign indicates polarity.  The returned tuple
    is ``(variable, is_positive)``.
    """

    var = abs(literal)
    pos = literal > 0
    return var, pos


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``Sat`` specification.

    Returns
    -------
    dict
        An instance of the ``Clique`` problem such that the answer to the
        Clique instance is *yes* iff the original SAT instance is *yes*.
    """

    # Validate the SAT instance – will raise InvalidInstance on malformed input.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: formula contains an empty clause → unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Produce a graph where k > n, guaranteeing a NO answer.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses → trivially satisfiable.
    if num_clauses == 0:
        # k = 0 satisfies the "k <= 0 is always yes" rule.
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices: each literal occurrence gets a unique id.
    # We'll keep a list mapping vertex id -> (clause_index, literal).
    vertex_info: List[Tuple[int, int]] = []  # (clause_idx, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n_vertices = len(vertex_info)
    # Edge list construction.
    edges: List[List[int]] = []
    # Helper to check compatibility of two literals.
    def compatible(lit1: int, lit2: int) -> bool:
        var1, pos1 = _literal_key(lit1)
        var2, pos2 = _literal_key(lit2)
        # Contradiction only when same variable with opposite polarity.
        return not (var1 == var2 and pos1 != pos2)

    for i in range(n_vertices):
        ci, lit_i = vertex_info[i]
        for j in range(i + 1, n_vertices):
            cj, lit_j = vertex_info[j]
            if ci == cj:
                # Vertices from the same clause must not be connected.
                continue
            if compatible(lit_i, lit_j):
                edges.append([i, j])

    # Validate the produced Clique instance before returning.
    clique_instance = {"n": n_vertices, "edges": edges, "k": num_clauses}
    Clique.validate(clique_instance)
    return clique_instance

