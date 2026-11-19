"""Reduction from 3‑SAT to Vertex Cover.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal ``li`` is an integer ``+v`` (variable ``v`` is true) or
``-v`` (variable ``v`` is false).  Every clause contains exactly three
different variables.

The target problem is :class:`VertexCover`.  An instance is a dictionary
``{"n": n, "edges": [[u, v], ...], "k": k}`` describing an undirected
graph on vertices ``0..n‑1`` and the integer ``k``.

We implement the classic polynomial‑time reduction (see e.g. Garey &
Johnson, *Computers and Intractability*).  For each variable ``x_i`` we
create two vertices ``i_T`` and ``i_F`` connected by an edge – picking one
endpoint of this edge corresponds to assigning the variable either true or
false.  For each clause we create a triangle of three new vertices; each
vertex of the triangle is connected to the variable‑literal vertex that
represents the literal appearing in the clause.

Formally, let ``m`` be the number of variables and ``c`` the number of
clauses.  Vertex IDs are assigned as follows:

* ``2*(i-1)``   – the *true* vertex for variable ``i`` (``i`` ranges 1..m)
* ``2*(i-1)+1`` – the *false* vertex for variable ``i``
* ``2*m + 3*j + k`` – the ``k``‑th vertex of clause ``j`` (``k`` = 0,1,2)

The edge set consists of:

1. Variable edges ``(i_T, i_F)`` for each ``i``.
2. For each clause ``j`` a triangle connecting its three clause vertices.
3. For each literal ``ℓ`` in clause ``j`` an edge between the clause vertex
   representing that literal and the appropriate variable literal vertex
   (true‑vertex for a positive literal, false‑vertex for a negative one).

The reduction uses ``k = m + 2*c``.  It is well‑known that the resulting
graph has a vertex cover of size at most ``k`` iff the original formula is
satisfiable.

The function ``reduce`` validates the source instance using the class
method ``ThreeSat.validate`` and then returns a valid target instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``VertexCover`` format such that the
        answer to the returned instance is *yes* exactly when the answer to
        ``instance`` is *yes*.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Vertex IDs for variable literals.
    # true_vertex[i]  = 2*(i-1)   (i from 1..m)
    # false_vertex[i] = 2*(i-1)+1
    def true_vertex(var: int) -> int:
        return 2 * (var - 1)

    def false_vertex(var: int) -> int:
        return 2 * (var - 1) + 1

    edges: List[List[int]] = []

    # 1. Variable edges.
    for var in range(1, m + 1):
        edges.append([true_vertex(var), false_vertex(var)])

    # Base index for clause vertices.
    base_clause = 2 * m

    # 2. Clause gadgets (triangles) and connections to variable literals.
    for j, clause in enumerate(clauses):
        # IDs of the three clause vertices.
        clause_ids = [base_clause + 3 * j + k for k in range(3)]

        # Add triangle edges.
        edges.append([clause_ids[0], clause_ids[1]])
        edges.append([clause_ids[0], clause_ids[2]])
        edges.append([clause_ids[1], clause_ids[2]])

        # Connect each clause vertex to the appropriate variable literal vertex.
        for lit, cid in zip(clause, clause_ids):
            var = abs(lit)
            if lit > 0:
                # positive literal → true vertex
                edges.append([cid, true_vertex(var)])
            else:
                # negative literal → false vertex
                edges.append([cid, false_vertex(var)])

    n = 2 * m + 3 * c
    k = m + 2 * c

    target_instance = {"n": n, "edges": edges, "k": k}
    # Validate the produced target instance.
    VertexCover.validate(target_instance)
    return target_instance

