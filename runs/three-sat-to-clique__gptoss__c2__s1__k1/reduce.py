"""Reduction from 3‑SAT to Clique.

The source problem is defined by :class:`problems.ThreeSat` (see the
docstring in *problems.py*).  An instance is a dictionary ``{"num_vars": m,
"clauses": [[l1, l2, l3], ...]}`` where each clause contains exactly three
distinct literals on distinct variables.  A literal is a signed integer:
``+v`` means variable *v* is true, ``-v`` means it is false.

The target problem is :class:`problems.Clique`.  Its instance format is
``{"n": n, "edges": [[u, v], ...], "k": k}`` where vertices are ``0..n-1``
and ``k`` is the size of the required clique (the question asks whether a
clique of *at least* ``k`` vertices exists).

Standard textbook reduction:

* For each clause we create three vertices – one for each literal.
* Vertices belonging to the *same* clause are **not** connected; a clique can
  therefore contain at most one literal from each clause.
* Vertices from *different* clauses are connected iff the corresponding
  literals are *compatible*, i.e. they do not contradict each other.  Two
  literals contradict when they refer to the same variable with opposite
  signs (``v`` and ``-v``).

With this construction a clique of size equal to the number of clauses
selects exactly one literal from each clause, and the compatibility condition
ensures that the selected literals can be simultaneously satisfied.  Hence the
original formula is satisfiable iff the graph contains a clique of size
``k = #clauses``.

Edge cases handled:

* An instance with **no clauses** is trivially satisfiable.  We output a graph
  with ``n = 0`` vertices and ``k = 0`` – by the definition of Clique, any
  ``k <= 0`` is a yes‑instance.
* The reduction works for any number of variables; the specification of the
  source guarantees ``m >= 3`` when there is at least one clause, but the code
  does not rely on that.

The function runs in polynomial time: it creates ``3 * C`` vertices and at
most ``9 * C * (C-1) / 2`` edges, where ``C`` is the number of clauses.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        An instance of the Clique problem: ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Vertex id for (clause_index, literal_position) is clause_index * 3 + pos
    n_vertices = num_clauses * 3
    edges: List[List[int]] = []

    # Pre‑compute the literal for each vertex to avoid repeated indexing.
    # literals[vertex_id] = literal value (signed int)
    literals: List[int] = []
    for clause in clauses:
        # Each clause is guaranteed to have exactly three literals.
        literals.extend(clause)

    # Build edges between compatible vertices from different clauses.
    for i in range(num_clauses):
        base_i = i * 3
        for j in range(i + 1, num_clauses):
            base_j = j * 3
            for li in range(3):
                lit_i = literals[base_i + li]
                for lj in range(3):
                    lit_j = literals[base_j + lj]
                    # Literals contradict iff they refer to the same variable
                    # with opposite signs.
                    if not (abs(lit_i) == abs(lit_j) and lit_i == -lit_j):
                        u = base_i + li
                        v = base_j + lj
                        # Store edge with smaller vertex first – not required
                        # but makes the output deterministic.
                        if u < v:
                            edges.append([u, v])
                        else:
                            edges.append([v, u])

    # The required clique size is the number of clauses.
    k = num_clauses
    return {"n": n_vertices, "edges": edges, "k": k}


__all__ = ["reduce"]
