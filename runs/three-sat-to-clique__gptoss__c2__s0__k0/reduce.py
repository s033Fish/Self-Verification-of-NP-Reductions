"""Reduction from 3‑SAT to Clique.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
following instance format (see the task description)::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Each literal ``li`` is an integer ``+v`` (meaning variable *v* is true) or
``-v`` (meaning variable *v* is false).  Every clause contains exactly three
distinct variables and does not contain both a variable and its negation.

The target problem is ``Clique`` with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 … n‑1`` and ``edges`` is a list of unordered pairs.

The classic polynomial‑time many‑one reduction works as follows.

* For each clause ``C_i`` we create three vertices, one for each literal in the
  clause.  Vertex identifiers are assigned consecutively.
* We connect two vertices belonging to *different* clauses unless the two
  corresponding literals are contradictory – i.e. they refer to the same
  variable with opposite signs.
* We set ``k`` to the number of clauses.  A clique of size ``k`` therefore
  selects exactly one vertex from each clause, and the non‑contradiction of the
  edges guarantees that the selected literals can be simultaneously satisfied.

Edge cases handled:

* **No clauses** – the formula is trivially satisfiable.  We output a graph with
  ``n = 0`` vertices, no edges and ``k = 0``.  By the definition of Clique, this
  instance is a yes‑instance.
* **k <= 0** – the target definition already treats this as a yes‑instance, so
  the above construction works for ``k = 0``.

The implementation below follows this construction and runs in ``O(N^2)``
time where ``N = 3 * #clauses`` – polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        above.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": k}`` that is a
        yes‑instance iff the original 3‑SAT instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Trivial case: no clauses → always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal in each clause.
    # Store for each vertex the (variable, sign) and the clause it belongs to.
    vertex_info: List[Tuple[int, bool, int]] = []  # (var, sign, clause_idx)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit)
            sign = lit > 0  # True for positive literal, False for negated
            vertex_info.append((var, sign, ci))

    n = len(vertex_info)
    edges: List[List[int]] = []

    # Build edges between vertices of different clauses unless they are
    # contradictory (same variable, opposite signs).
    for i in range(n):
        var_i, sign_i, clause_i = vertex_info[i]
        for j in range(i + 1, n):
            var_j, sign_j, clause_j = vertex_info[j]
            if clause_i == clause_j:
                # Vertices from the same clause must not be connected.
                continue
            # Contradictory if same variable with opposite signs.
            if var_i == var_j and sign_i != sign_j:
                continue
            edges.append([i, j])

    # The required clique size is exactly the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

