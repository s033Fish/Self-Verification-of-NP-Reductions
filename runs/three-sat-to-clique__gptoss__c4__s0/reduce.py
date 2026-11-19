"""Reduction from 3-SAT to Clique.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
literal ``li`` is an integer ``+v`` (variable ``v`` set to true) or ``-v``
(variable ``v`` set to false).  Every clause contains exactly three literals on
distinct variables.

The target problem is ``Clique`` with instance format ``{"n": n, "edges":
[[u, v], ...], "k": k}``.  Vertices are numbered ``0`` … ``n-1`` and the edge
list contains each undirected edge exactly once with ``u < v``.

The classic polynomial‑time reduction constructs a graph with three vertices
per clause – one for each literal.  Two vertices from *different* clauses are
connected by an edge iff the corresponding literals are *compatible*, i.e. they
are not complementary (they do not refer to the same variable with opposite
signs).  A clique of size equal to the number of clauses corresponds to a
selection of one literal per clause that can be simultaneously satisfied.

The ``reduce`` function implements this construction.  Edge cases are handled
as follows:

* An instance with no clauses is trivially satisfiable.  We reduce it to a
  Clique instance with ``k = 0`` (always a yes‑instance) – the smallest such
  graph is ``{"n": 0, "edges": [], "k": 0}``.
* The input is assumed to be valid according to ``problems.py``; the function
  does not perform extensive validation to keep the implementation simple and
  fast.

The reduction runs in time ``O(c^2)`` where ``c`` is the number of clauses, which
is polynomial in the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        above.

    Returns
    -------
    dict
        A Clique instance dictionary ``{"n": n, "edges": [...], "k": k}``.
    """
    num_vars = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: no clauses → always satisfiable.
    if not clauses:
        # k = 0 is always a yes‑instance for Clique.
        return {"n": 0, "edges": [], "k": 0}

    c = len(clauses)  # number of clauses
    n = 3 * c          # three vertices per clause
    k = c              # we look for a clique of size equal to the number of clauses

    # Map (clause_index, literal_position) -> vertex id
    def vertex_id(ci: int, li: int) -> int:
        return ci * 3 + li

    edges: List[List[int]] = []
    # Build edges between vertices of different clauses if literals are compatible.
    for i in range(c):
        for j in range(i + 1, c):
            clause_i = clauses[i]
            clause_j = clauses[j]
            for li, lit_i in enumerate(clause_i):
                for lj, lit_j in enumerate(clause_j):
                    # literals are incompatible only when they refer to the same
                    # variable with opposite signs.
                    var_i = abs(lit_i)
                    var_j = abs(lit_j)
                    if var_i == var_j and lit_i != lit_j:
                        # contradictory literals – do not add an edge
                        continue
                    u = vertex_id(i, li)
                    v = vertex_id(j, lj)
                    # Ensure u < v for canonical representation
                    if u < v:
                        edges.append([u, v])
                    else:
                        edges.append([v, u])

    # Remove potential duplicate edges (should not happen, but guard against it)
    unique_edges = {tuple(e) for e in edges}
    edge_list = [list(e) for e in sorted(unique_edges)]

    return {"n": n, "edges": edge_list, "k": k}

