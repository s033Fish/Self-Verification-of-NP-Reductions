"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined by :class:`Sat` in ``problems.py`` and the
target problem by :class:`Clique`.  Both classes only provide a ``validate``
method – they do **not** provide solvers.  This file implements a polynomial‑
time many‑one reduction ``reduce(instance)`` that maps a SAT instance to a
Clique instance such that the answer (yes/no) is preserved.

Classic reduction:
    * For every literal occurrence in each clause we create a vertex.
    * Two vertices are connected by an edge iff they belong to *different*
      clauses and the corresponding literals are **not** contradictory
      (i.e. they are not of the form ``v`` and ``-v`` for the same variable).
    * The parameter ``k`` of the Clique instance is set to the number of
      clauses.  A clique of size ``k`` corresponds to selecting one literal
      from each clause that are pairwise non‑contradictory, which yields a
      satisfying assignment.

Edge‑case handling mirrors the specification in the doc‑string of ``Sat``:

    * **No clauses** – the formula is trivially satisfiable.  We return a
      graph with ``k = 0`` (always a yes‑instance for Clique).
    * **Empty clause** – the formula is unsatisfiable.  We return a graph
      where ``k > n`` (e.g. ``n = 0, k = 1``) which is always a no‑instance.

The implementation is straightforward and runs in ``O(V^2)`` time where
``V`` is the total number of literal occurrences – polynomial in the size of
the input.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, Clique


def _has_empty_clause(clauses: List[List[int]]) -> bool:
    """Return ``True`` if any clause is the empty list.

    The SAT definition treats an empty clause as unsatisfiable.
    """
    return any(len(c) == 0 for c in clauses)


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``Sat`` format – ``{"num_vars": m,
        "clauses": [[literal, ...], ...]}``.

    Returns
    -------
    dict
        An instance of ``Clique`` – ``{"n": n, "edges": [[u, v], ...],
        "k": k}`` – such that the SAT instance is satisfiable iff the
        Clique instance contains a clique of size at least ``k``.
    """
    # Validate the source instance (will raise InvalidInstance on malformed
    # input).  The validation is cheap and ensures we can rely on the format.
    Sat.validate(instance)

    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: formula contains an empty clause → unsatisfiable.
    if _has_empty_clause(clauses):
        # Return a graph where k > n, guaranteeing a NO answer.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses → trivially satisfiable.
    if len(clauses) == 0:
        # k = 0 is always a YES instance for Clique.
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices: each literal occurrence gets a unique vertex id.
    # We also keep track of the clause index for each vertex.
    vertex_literals: List[int] = []  # literal value for each vertex
    vertex_clause: List[int] = []    # clause index for each vertex
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_literals.append(lit)
            vertex_clause.append(ci)

    n = len(vertex_literals)
    k = len(clauses)

    # Construct edges between vertices of different clauses that are not
    # contradictory.
    edges: List[Tuple[int, int]] = []
    for i in range(n):
        ci = vertex_clause[i]
        li = vertex_literals[i]
        for j in range(i + 1, n):
            cj = vertex_clause[j]
            if ci == cj:
                # Vertices from the same clause must not be connected.
                continue
            lj = vertex_literals[j]
            # Contradiction occurs when literals are opposite on the same
            # variable, i.e., li == -lj.
            if li == -lj:
                continue
            edges.append((i, j))

    # Convert edges to the required list-of-lists representation.
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]

    result = {"n": n, "edges": edge_list, "k": k}
    # Validate the target instance before returning.
    Clique.validate(result)
    return result

