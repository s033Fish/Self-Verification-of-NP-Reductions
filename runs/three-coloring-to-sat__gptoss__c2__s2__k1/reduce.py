"""Reduction from 3-Coloring to SAT.

The source problem is ``ThreeColoring`` with an instance format::

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered ``0..n-1`` and ``edges`` is a list of unordered
pairs.  The target problem is ``Sat`` with an instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1..m`` and a literal is represented by an integer:
``+v`` (positive integer) means the variable ``v`` is true, ``-v`` (negative
integer) means the variable ``v`` is false.

The reduction creates three Boolean variables for each vertex, one for each
colour (colour 1, 2 and 3).  The mapping from a vertex ``v`` and colour ``c``
to a SAT variable index is ``v * 3 + c`` (with ``c`` in ``{1,2,3}``).  The
total number of variables is therefore ``3 * n``.

Constraints encoded as CNF clauses:

1. **Each vertex receives at least one colour** – a clause containing the
   three positive literals for that vertex.
2. **Each vertex receives at most one colour** – for each pair of distinct
   colours ``c1, c2`` add a clause ``(¬x_{v,c1} ∨ ¬x_{v,c2})``.
3. **Adjacent vertices cannot share a colour** – for every edge ``(u, v)``
   and every colour ``c`` add a clause ``(¬x_{u,c} ∨ ¬x_{v,c})``.

These clauses are sufficient: any satisfying assignment corresponds to a
proper 3‑colouring of the graph, and any proper 3‑colouring can be turned into
an assignment that satisfies all clauses.

The function runs in time polynomial in the size of the input graph (linear
in the number of vertices and edges).  Edge cases such as ``n == 0`` are
handled automatically – the produced SAT instance will have ``0`` variables
and ``0`` clauses, which is trivially satisfiable.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[List[int]]}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}``
    """
    n = instance.get("n", 0)
    edges = instance.get("edges", [])

    # Number of SAT variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # Helper to compute variable index for vertex v (0‑based) and colour c (1‑based).
    def var(v: int, c: int) -> int:
        return v * 3 + c  # results in 1‑based index because v>=0 and c>=1

    # 1. At least one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 1), var(v, 2), var(v, 3)])

    # 2. At most one colour per vertex (pairwise different).
    for v in range(n):
        # (¬x_{v,1} ∨ ¬x_{v,2}), (¬x_{v,1} ∨ ¬x_{v,3}), (¬x_{v,2} ∨ ¬x_{v,3})
        clauses.append([-var(v, 1), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 3)])
        clauses.append([-var(v, 2), -var(v, 3)])

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        # Ensure each colour differs across the edge.
        for c in (1, 2, 3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

