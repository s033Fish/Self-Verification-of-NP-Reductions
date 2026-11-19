"""Reduction from 3‑SAT to Vertex Cover.

The source problem (``ThreeSat``) is described in ``problems.py`` as a
dictionary with the keys ``num_vars`` and ``clauses``.  A clause is a list
of three literals where a literal is an integer ``+v`` (meaning variable *v*
+is true) or ``-v`` (meaning variable *v* is false).

The target problem (``VertexCover``) expects a dictionary with the keys
``n`` (number of vertices), ``edges`` (list of undirected edges) and ``k``
+(size bound for the vertex cover).

The classic polynomial‑time reduction works as follows:

* **Variable gadget** – for each variable *i* (1‑based) create two vertices
  ``t_i`` (represents the literal ``+i``) and ``f_i`` (represents ``-i``) and
  add the edge ``(t_i, f_i)``.  Selecting exactly one of the two vertices in
  a minimum vertex cover corresponds to assigning a truth value to the
  variable.

* **Clause gadget** – for each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` create three fresh
  vertices ``c1, c2, c3`` forming a triangle (edges ``(c1,c2), (c2,c3),
  (c3,c1)``).  Each ``ck`` is connected to the vertex that represents the
  corresponding literal ``ℓk``.

In any vertex cover at least one endpoint of every edge must be chosen.
For a triangle at least two vertices are required, therefore a cover of
size ``|vars| + 2·|clauses|`` is the theoretical minimum.  Such a cover exists
iff the original 3‑SAT formula is satisfiable: pick for each variable the
vertex that corresponds to the true literal, and for each clause leave the
vertex that corresponds to a satisfied literal uncovered (its incident edge
to the true literal vertex is already covered).

The reduction constructs the graph described above and returns the instance
``{"n": n, "edges": edges, "k": k}`` where ``k = num_vars + 2 * len(clauses)``.
The implementation runs in time linear in the size of the input, i.e. it
is polynomial.
"""

from typing import List, Dict, Any


def _literal_vertex(literal: int, num_vars: int) -> int:
    """Return the vertex index representing ``literal``.

    Vertices for variable *i* are allocated as follows::

        true  ( +i ) -> 2 * (i-1)
        false ( -i ) -> 2 * (i-1) + 1

    ``literal`` is a signed integer where the sign encodes the polarity.
    """
    var = abs(literal)
    base = 2 * (var - 1)
    return base if literal > 0 else base + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``num_vars`` (int) and ``clauses`` (list of
        list of three literals).

    Returns
    -------
    dict
        A Vertex‑Cover instance as described in ``problems.py``.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex numbering:
    #   0 .. 2*m-1   – variable literal vertices (true then false for each var)
    #   following    – clause vertices, three per clause.
    var_vertices = 2 * m
    clause_vertices_start = var_vertices
    total_vertices = var_vertices + 3 * len(clauses)

    edges_set = set()

    # Variable edges (t_i, f_i)
    for i in range(1, m + 1):
        true_v = 2 * (i - 1)
        false_v = true_v + 1
        edges_set.add(tuple(sorted((true_v, false_v))))

    # Clause gadgets
    for idx, clause in enumerate(clauses):
        # indices of the three clause vertices
        c1 = clause_vertices_start + 3 * idx
        c2 = c1 + 1
        c3 = c1 + 2

        # triangle edges
        edges_set.add(tuple(sorted((c1, c2))))
        edges_set.add(tuple(sorted((c2, c3))))
        edges_set.add(tuple(sorted((c3, c1))))

        # connect each clause vertex to the corresponding literal vertex
        for lit, c_vert in zip(clause, (c1, c2, c3)):
            lit_vert = _literal_vertex(lit, m)
            edges_set.add(tuple(sorted((c_vert, lit_vert))))

    # Convert edge set to list of [u, v]
    edges: List[List[int]] = [list(e) for e in edges_set]

    k = m + 2 * len(clauses)

    return {"n": total_vertices, "edges": edges, "k": k}

