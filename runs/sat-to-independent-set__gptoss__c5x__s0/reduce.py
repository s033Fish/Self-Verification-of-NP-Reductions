"""Reduction from SAT to Independent Set.

The source problem is SAT (CNF satisfiability) as defined in ``problems.py``.
The target problem is Independent Set.

For a SAT instance with ``m`` variables and ``c`` clauses we construct a
graph with one vertex for each literal occurring in a clause.  Vertices that
belong to the same clause are made adjacent (a clique) so that an independent
set can contain **at most** one literal from each clause.  Additionally we add
edges between contradictory literals (``x`` and ``¬x``) that appear in
different clauses – such a pair cannot be chosen simultaneously in a
satisfying assignment.

An independent set of size ``c`` therefore corresponds exactly to a choice of
one literal from every clause that does not contain a conflict, i.e. a
truth‑assignment satisfying the formula.  The construction runs in polynomial
time.

Edge‑case handling:
* If the formula contains an empty clause the instance is unsatisfiable – we
  output a graph where ``k`` is larger than the number of vertices, guaranteeing
  a ``no`` answer.
* If there are no clauses the formula is trivially satisfiable – we output a
  trivial graph with ``k = 0`` (always a yes).

The function ``reduce`` performs the transformation and returns a dictionary
compatible with the ``IndependentSet`` problem definition.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, IndependentSet


def _unsat_instance() -> Dict:
    """Return a deliberately unsatisfiable Independent‑Set instance.

    The instance has no vertices and asks for an independent set of size 1,
    which is impossible.
    """
    return {"n": 0, "edges": [], "k": 1}


def _trivial_sat_instance() -> Dict:
    """Return a trivially satisfiable Independent‑Set instance.

    With ``k = 0`` the answer is always yes.
    """
    return {"n": 0, "edges": [], "k": 0}


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``IndependentSet`` format such that the
        answer to the returned instance is *yes* iff the answer to the input
        SAT instance is *yes*.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: formula contains an empty clause → unsatisfiable.
    if any(len(clause) == 0 for clause in clauses):
        return _unsat_instance()

    num_clauses = len(clauses)
    # Edge case: no clauses → always satisfiable.
    if num_clauses == 0:
        return _trivial_sat_instance()

    # ---------------------------------------------------------------------
    # Build vertices. One vertex per literal occurrence (duplicates kept).
    # ``vertices`` stores (clause_index, literal) for each vertex.
    vertices: List[Tuple[int, int]] = []
    # ``clause_vertices[ci]`` holds vertex indices belonging to clause ci.
    clause_vertices: List[List[int]] = []
    for ci, clause in enumerate(clauses):
        clause_vertices.append([])
        for lit in clause:
            idx = len(vertices)
            vertices.append((ci, lit))
            clause_vertices[ci].append(idx)

    n = len(vertices)
    edges: List[List[int]] = []

    # ---------------------------------------------------------------------
    # 1. Make each clause a clique (at most one literal per clause).
    for idxs in clause_vertices:
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                edges.append([idxs[i], idxs[j]])

    # ---------------------------------------------------------------------
    # 2. Add edges between contradictory literals from different clauses.
    #    Collect positive and negative occurrences per variable.
    pos: Dict[int, List[int]] = {}
    neg: Dict[int, List[int]] = {}
    for idx, (ci, lit) in enumerate(vertices):
        var = abs(lit)
        if lit > 0:
            pos.setdefault(var, []).append(idx)
        else:
            neg.setdefault(var, []).append(idx)

    for var in range(1, num_vars + 1):
        for p_idx in pos.get(var, []):
            for n_idx in neg.get(var, []):
                # Skip if same clause – already connected by clause clique.
                if vertices[p_idx][0] != vertices[n_idx][0]:
                    edges.append([p_idx, n_idx])

    # Target asks for an independent set of size at least the number of clauses.
    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

