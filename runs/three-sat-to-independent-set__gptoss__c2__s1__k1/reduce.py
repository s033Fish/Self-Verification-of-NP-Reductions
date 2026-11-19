"""Reduction from 3‑SAT to Independent Set.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is a string ``"+v"`` (variable *v* is true) or
``"-v"`` (variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``IndependentSet`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic one used in textbooks:

* For each clause we create a triangle (3 vertices, all mutually
  adjacent).  Selecting at most one vertex from each triangle ensures we
  pick at most one literal per clause.
* Vertices corresponding to contradictory literals (``+x`` vs ``-x``)
  are connected by an edge.  This prevents the independent set from
  containing both a variable and its negation.
* We ask for an independent set of size exactly the number of clauses
  (``k = |clauses|``).  Such a set exists iff the original formula is
  satisfiable.

The construction runs in polynomial time: we create ``3·C`` vertices
(``C`` = number of clauses) and at most ``3·C`` intra‑clause edges plus a
quadratic number of inter‑clause edges, which is still polynomial in the
input size.

The ``reduce`` function below implements this construction.  It does not
perform any validation or solving; it simply translates the instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _parse_literal(lit: str) -> Tuple[int, bool]:
    """Return ``(var, sign)`` where ``sign`` is ``True`` for ``+`` and ``False`` for ``-``.

    The literal format is guaranteed by the problem statement, but we
    defensively handle a leading ``+`` or ``-`` followed by an integer.
    """
    if not lit:
        raise ValueError("Empty literal")
    sign = lit[0] == "+"
    var = int(lit[1:])
    return var, sign


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """
    clauses: List[List[str]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Vertex id assignment: each literal in each clause gets a unique id.
    # We store a mapping from (clause_index, position) -> (var, sign, vertex_id).
    vertex_info: List[Tuple[int, bool, int]] = []  # (var, sign, id)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            var, sign = _parse_literal(lit)
            # placeholder id, will be set later
            vertex_info.append((var, sign, -1))

    # Assign sequential ids now.
    for idx in range(len(vertex_info)):
        var, sign, _ = vertex_info[idx]
        vertex_info[idx] = (var, sign, idx)

    n = len(vertex_info)
    edges: List[List[int]] = []

    # Intra‑clause edges: each clause forms a triangle.
    for ci in range(num_clauses):
        base = ci * 3
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    # Inter‑clause contradictory edges.
    # For every pair of vertices from different clauses, add an edge if they are opposite literals of the same variable.
    for i in range(n):
        var_i, sign_i, _ = vertex_info[i]
        for j in range(i + 1, n):
            var_j, sign_j, _ = vertex_info[j]
            # Skip if same clause (already handled) – they are within same block of 3.
            if i // 3 == j // 3:
                continue
            if var_i == var_j and sign_i != sign_j:
                edges.append([i, j])

    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

