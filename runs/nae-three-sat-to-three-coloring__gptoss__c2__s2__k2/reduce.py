"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (``NaeThreeSat``) is defined in ``problems.py`` as a
dictionary with the keys ``"num_vars"`` and ``"clauses"`` where each clause
contains exactly three literals.  A literal is represented by an integer:
``+v`` means the variable ``v`` is true, ``-v`` means the variable ``v`` is false.

The target problem (``ThreeColoring``) expects a graph given by the number of
vertices ``n`` and a list of undirected edges ``edges`` where each edge is a
pair ``[u, v]`` with ``0 <= u, v < n`` and ``u != v``.

The reduction works in two stages:

1. **NAE‑3‑SAT  →  3‑SAT**
   A clause is satisfied in the NAE sense iff it is satisfied by the ordinary
   clause *and* by its negation.  Therefore each NAE clause ``(l1 ∨ l2 ∨ l3)``
   is replaced by the two 3‑SAT clauses ``[l1, l2, l3]`` and ``[-l1, -l2, -l3]``.

2. **3‑SAT  →  3‑Coloring** (standard reduction)
   *Vertices*
   - Three special vertices form a triangle and represent the three colours:
     ``0`` – colour *True*, ``1`` – colour *False*, ``2`` – colour *Base*.
   - For each variable ``x`` we create two vertices ``x_T`` and ``x_F``
     (indices ``3 + 2*(x-1)`` and ``4 + 2*(x-1)``).  Both are adjacent to the
     Base vertex ``2`` and to each other.  Consequently they must be coloured
     with the two distinct colours *True* and *False*, encoding the truth
     assignment of the variable.
   - For each 3‑SAT clause we create a *clause gadget*: three new vertices
     forming a triangle.  Each of those vertices is adjacent to the Base
     vertex and to the vertex representing the corresponding literal (the
     ``x_T`` vertex for a positive literal ``+x`` and the ``x_F`` vertex for a
     negative literal ``-x``).  The gadget forces that not all three literals
     can be false; otherwise the three clause vertices would be forced to the
     colour *True* which is impossible because they form a triangle.

The construction is polynomial in the size of the input (linear in the
number of variables and clauses).  The returned graph is 3‑colourable iff the
original NAE‑3‑SAT instance is satisfiable.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _add_edge(edges: List[List[int]], u: int, v: int) -> None:
    """Add an undirected edge ``[u, v]`` ensuring ``u < v``.

    The caller guarantees that the edge does not already exist; the function
    merely normalises the order to keep the representation consistent.
    """
    if u == v:
        raise ValueError("self-loops are not allowed")
    if u > v:
        u, v = v, u
    edges.append([u, v])


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` suitable for the ``ThreeColoring``
        problem definition.
    """
    m: int = instance["num_vars"]
    nae_clauses: List[List[int]] = instance["clauses"]

    # ---------------------------------------------------------------------
    # Stage 1 – convert NAE‑3‑SAT to ordinary 3‑SAT by adding the negated
    # clause for each original clause.
    # ---------------------------------------------------------------------
    sat_clauses: List[List[int]] = []
    for clause in nae_clauses:
        # Original clause
        sat_clauses.append(clause[:])
        # Negated clause – flip the sign of each literal
        sat_clauses.append([-lit for lit in clause])

    # ---------------------------------------------------------------------
    # Stage 2 – build the graph for the 3‑SAT instance.
    # ---------------------------------------------------------------------
    edges: List[List[int]] = []

    # Special triangle vertices: 0 (True), 1 (False), 2 (Base)
    _add_edge(edges, 0, 1)
    _add_edge(edges, 1, 2)
    _add_edge(edges, 2, 0)

    # Helper to retrieve the vertex index for the true/false representation
    # of a variable.
    def var_true(v: int) -> int:
        return 3 + 2 * (v - 1)

    def var_false(v: int) -> int:
        return 3 + 2 * (v - 1) + 1

    # Variable gadgets
    for var in range(1, m + 1):
        vt = var_true(var)
        vf = var_false(var)
        # Connect each to the Base vertex (2)
        _add_edge(edges, vt, 2)
        _add_edge(edges, vf, 2)
        # Edge between the two literals forces opposite colours
        _add_edge(edges, vt, vf)

    # Clause gadgets
    next_vid = 3 + 2 * m  # first unused vertex index
    for clause in sat_clauses:
        clause_vertices = []
        for lit in clause:
            cv = next_vid
            next_vid += 1
            clause_vertices.append(cv)
            # Connect to Base vertex
            _add_edge(edges, cv, 2)
            var = abs(lit)
            if lit > 0:
                # Positive literal → connect to the "true" vertex of the variable
                _add_edge(edges, cv, var_true(var))
            else:
                # Negative literal → connect to the "false" vertex
                _add_edge(edges, cv, var_false(var))
        # Form a triangle among the three clause vertices
        a, b, c = clause_vertices
        _add_edge(edges, a, b)
        _add_edge(edges, b, c)
        _add_edge(edges, a, c)

    n = next_vid
    return {"n": n, "edges": edges}

