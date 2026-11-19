"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...]}

where ``n`` is the number of vertices (labelled ``0..n-1``) and each edge is
an unordered pair of distinct vertices.

The target problem (OneInThreeSat) expects an instance of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where variables are numbered from ``1`` to ``m`` and each clause contains
exactly three *different* positive literals.  A clause is satisfied iff **exactly
one** of its three literals is true.

The reduction is classic and runs in polynomial time.

For every vertex ``v`` we create three Boolean variables ``R_v, G_v, B_v``
representing the colour assigned to ``v``.  The clause ``[R_v, G_v, B_v]`` forces
exactly one of the three colours to be chosen for ``v``.

For every edge ``(u, v)`` and for each colour ``c`` we must forbid ``u`` and ``v``
from both receiving colour ``c``.  This is achieved with an auxiliary variable
``X_{u,v,c}`` and the clause ``[c_u, c_v, X_{u,v,c}]``.  The clause is satisfied
iff exactly one of its three literals is true.  Consequently:

* If both ``c_u`` and ``c_v`` are true, the clause cannot be satisfied (two
  true literals).
* If exactly one of ``c_u`` or ``c_v`` is true, ``X_{u,v,c}`` must be false.
* If neither ``c_u`` nor ``c_v`` is true, ``X_{u,v,c}`` must be true.

Thus the clause forbids the two endpoints from sharing the same colour while
still allowing the assignment to satisfy the clause by setting the auxiliary
variable appropriately.

The construction uses:

* ``3 * n`` variables for the vertex colours.
* ``3 * |E|`` auxiliary variables (one per edge per colour).

The total number of variables ``m`` is therefore ``3 * n + 3 * len(edges)``.

The function ``reduce`` implements this transformation and returns the target
instance.  It runs in time linear in the size of the input graph, which is
polynomial.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a Positive 1-in-3 SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs).

    Returns
    -------
    dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` suitable for
        the ``OneInThreeSat`` problem.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: empty graph – produce a trivially satisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Helper to map a vertex and colour offset to a variable number.
    # Offsets: 0 -> Red, 1 -> Green, 2 -> Blue.
    def var(v: int, offset: int) -> int:
        return 3 * v + offset + 1  # +1 because variables start at 1

    clauses: List[List[int]] = []

    # 1. Exactly one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. Edge constraints using auxiliary variables.
    # We'll allocate auxiliary variables after the vertex variables.
    aux_counter = 3 * n  # number of variables used so far
    for (u, v) in edges:
        for offset in range(3):
            aux_counter += 1
            aux_var = aux_counter
            clauses.append([var(u, offset), var(v, offset), aux_var])

    num_vars = aux_counter
    return {"num_vars": num_vars, "clauses": clauses}

