"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  Literals
are represented by signed integers: ``+v`` means the variable ``v`` is true
and ``-v`` means it is false.

The target problem is ``VertexCover`` with an instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic Karp reduction:

* For each variable ``x_i`` create two vertices ``i_T`` and ``i_F`` (true and
  false) and add the edge ``(i_T, i_F)``.
* For each clause ``C_j = (ℓ_1 ∨ ℓ_2 ∨ ℓ_3)`` create three vertices forming a
  triangle.  The three vertices are connected pairwise.
* Connect each clause‑vertex representing literal ``ℓ`` to the *opposite*
  literal vertex of the variable.  If ``ℓ`` is ``+v`` (i.e. ``x_v``), we connect
  the clause vertex to ``v_F``; if ``ℓ`` is ``-v`` we connect to ``v_T``.

If the formula has ``m`` variables and ``c`` clauses the construction uses
``2*m + 3*c`` vertices.  The parameter ``k`` is set to ``m + 2*c``.  It is well
known that the original 3‑SAT instance is satisfiable iff the resulting graph
has a vertex cover of size at most ``k``.

The ``reduce`` function performs this construction in polynomial time and
returns the target instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}``
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    c: int = len(clauses)

    # Vertex indexing:
    #   variable true  vertex for i (1‑based) -> 2*(i-1)
    #   variable false vertex for i          -> 2*(i-1) + 1
    # Clause vertices start after the 2*m variable vertices.
    clause_offset = 2 * m

    edges: List[List[int]] = []

    # 1. Variable edges (xi, ¬xi)
    for i in range(1, m + 1):
        true_v = 2 * (i - 1)
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # 2. Clause triangles and connections to variable literals
    for j, clause in enumerate(clauses):
        # clause vertices indices
        base = clause_offset + 3 * j
        v0, v1, v2 = base, base + 1, base + 2
        # triangle edges
        edges.append([v0, v1])
        edges.append([v1, v2])
        edges.append([v2, v0])

        # connections to opposite literals
        for pos, lit in enumerate(clause):
            clause_vertex = base + pos
            var = abs(lit)
            if var == 0:
                continue
            # Determine the vertex representing the *negation* of the literal.
            if lit > 0:
                # literal is x_var, connect to false vertex
                opposite = 2 * (var - 1) + 1
            else:
                # literal is ¬x_var, connect to true vertex
                opposite = 2 * (var - 1)
            edges.append([clause_vertex, opposite])

    n = 2 * m + 3 * c
    k = m + 2 * c

    return {"n": n, "edges": edges, "k": k}

