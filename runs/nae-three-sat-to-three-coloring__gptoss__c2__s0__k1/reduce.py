"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (``NaeThreeSat``) expects an instance of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable ``v`` is true) or
``-v`` (variable ``v`` is false).  A clause is satisfied in the *not‑all‑
equal* sense iff it contains at least one true literal and at least one
false literal.

The target problem (``ThreeColoring``) expects a graph given by the number
of vertices ``n`` and a list of undirected edges ``[[u, v], ...]`` where the
vertices are numbered ``0 … n‑1``.

We construct a graph that is 3‑colourable exactly when the NAE‑3‑SAT formula
has a not‑all‑equal satisfying assignment.  The construction follows the
standard textbook reduction (see, e.g., Garey & Johnson, *Computers and
Intractability*).  The three colours are interpreted as:

* ``0`` – a distinguished *base* colour (often called ``B``),
* ``1`` – logical ``TRUE``,
* ``2`` – logical ``FALSE``.

Construction details
---------------------
* **Base vertex** – vertex ``0``.  It will be forced to take the base colour.
* **Variable gadget** – for each variable ``i`` (1‑based) we create two
  vertices ``ti`` (true) and ``fi`` (false).  Both are adjacent to the base
  vertex, so they cannot use the base colour.  An edge between ``ti`` and
  ``fi`` forces them to receive different colours, i.e. one is ``TRUE`` and
  the other ``FALSE``.
* **Clause gadget** – for each clause ``(ℓ1, ℓ2, ℓ3)`` we introduce three
  fresh vertices ``c1, c2, c3`` that form a triangle.  A triangle in a
  3‑colouring must use all three colours, so the three clause vertices are
  forced to be pairwise different.  Vertex ``ck`` is also connected to the
  literal vertex that corresponds to ``ℓk`` (the true‑vertex for a positive
  literal and the false‑vertex for a negative literal).  Because ``ck``
  cannot share a colour with its adjacent literal vertex, the three literal
  vertices cannot all be the same colour – otherwise the three clause
  vertices would be forced to use the *same* set of colours, contradicting
  the triangle requirement.  Consequently the clause is satisfied in the
  NAE sense.

The reduction runs in polynomial time and produces a graph with

``n = 1 + 2*m + 3*|clauses|`` vertices and a linear number of edges.

The ``reduce`` function below implements this construction.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).

    Returns
    -------
    dict
        A graph instance suitable for the ``ThreeColoring`` problem with the
        keys ``"n"`` and ``"edges"``.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex layout:
    # 0                         -> base vertex
    # 1,2,...,2*m               -> variable literals (true/false)
    #   true_i  = 1 + 2*(i-1)
    #   false_i = 2 + 2*(i-1)
    # remaining vertices        -> clause gadget vertices, three per clause

    base = 0
    def true_vertex(var: int) -> int:
        return 1 + 2 * (var - 1)

    def false_vertex(var: int) -> int:
        return 2 + 2 * (var - 1)

    clause_start = 1 + 2 * m  # first index for clause vertices
    edges: List[List[int]] = []

    # Helper to add an undirected edge with canonical ordering (u < v)
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append([u, v])

    # Base connections and variable gadgets
    for var in range(1, m + 1):
        tv = true_vertex(var)
        fv = false_vertex(var)
        # Connect both literals to base
        add_edge(base, tv)
        add_edge(base, fv)
        # Connect true and false literals together (force opposite colours)
        add_edge(tv, fv)

    # Clause gadgets
    for idx, clause in enumerate(clauses):
        if len(clause) != 3:
            # The problem definition guarantees length 3, but we guard
            # against malformed input.
            continue
        c0 = clause_start + 3 * idx
        c1 = c0 + 1
        c2 = c0 + 2
        # triangle among clause vertices
        add_edge(c0, c1)
        add_edge(c1, c2)
        add_edge(c2, c0)
        # connect each clause vertex to the corresponding literal vertex
        for lit, cv in zip(clause, (c0, c1, c2)):
            var = abs(lit)
            if lit > 0:
                lit_vertex = true_vertex(var)
            else:
                lit_vertex = false_vertex(var)
            add_edge(lit_vertex, cv)

    n_vertices = clause_start + 3 * len(clauses)
    return {"n": n_vertices, "edges": edges}

