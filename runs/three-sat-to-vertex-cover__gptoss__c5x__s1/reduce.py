"""Reduction from 3‑SAT to Vertex Cover.

The construction follows the classic textbook reduction:

* For each variable *x_i* we create two vertices *v_i* (representing
  *x_i = True*) and *¬v_i* (representing *x_i = False*) and add the edge
  ``[v_i, ¬v_i]``.
* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a triangle of three new
  vertices ``c_{j,1}, c_{j,2}, c_{j,3}`` and connect them pairwise.
* For each literal ``ℓ`` in a clause we connect the corresponding clause
  vertex to the *opposite* literal vertex of the variable gadget.  In other
  words, a positive literal ``+i`` is connected to the *false* vertex of
  variable ``i`` and a negative literal ``-i`` is connected to the *true*
  vertex of ``i``.

With this graph the minimum vertex‑cover size is ``m + 2·C`` where ``m`` is
the number of variables and ``C`` the number of clauses.  A cover of that
size exists iff the original formula is satisfiable.

The ``reduce`` function validates the source instance using the provided
``ThreeSat.validate`` method, builds the graph described above and returns
an instance of the target problem (Vertex Cover) with ``k = m + 2·C``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary matching the format required by ``ThreeSat``:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance – this will raise ``InvalidInstance``
    # if the input is malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    C: int = len(clauses)

    # Vertex indices:
    #   variable vertices:   0 .. 2*m-1   (true = 2*i, false = 2*i+1)
    #   clause vertices:    2*m .. 2*m + 3*C - 1
    clause_offset = 2 * m

    edges: List[List[int]] = []

    # 1. Variable edges (v_i, ¬v_i)
    for i in range(m):
        true_v = 2 * i
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # 2. Clause triangles and connections to variable gadgets
    for j, clause in enumerate(clauses):
        # indices of the three clause vertices for this clause
        base = clause_offset + 3 * j
        c_vertices = [base, base + 1, base + 2]

        # a) triangle edges among the three clause vertices
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])

        # b) connect each clause vertex to the opposite literal vertex
        for lit, cv in zip(clause, c_vertices):
            var = abs(lit) - 1  # zero‑based variable index
            true_v = 2 * var
            false_v = true_v + 1
            opposite = false_v if lit > 0 else true_v
            edges.append([cv, opposite])

    n = 2 * m + 3 * C
    k = m + 2 * C
    target_instance: Dict = {"n": n, "edges": edges, "k": k}
    VertexCover.validate(target_instance)
    return target_instance

