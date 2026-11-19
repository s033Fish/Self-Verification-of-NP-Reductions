"""Reduction from 3-Coloring to SAT.

The source problem ``ThreeColoring`` is defined as follows (see ``problems.py``):

    Instance: {"n": n, "edges": [[u, v], ...]}
    Vertices are numbered 0..n-1. An edge ``[u, v]`` means the two vertices must
    receive different colours.  The question is whether the vertices can be
    coloured with three colours such that adjacent vertices receive distinct
    colours.

The target problem ``Sat`` expects an instance of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where variables are numbered 1..m and a *literal* is a positive integer ``v``
for the variable being true or a negative integer ``-v`` for the variable being
false.  A clause is satisfied if at least one of its literals is true.

The classic polynomial‑time reduction introduces three Boolean variables for each
vertex, one for each colour.  Let ``x_{i,c}`` denote the variable that is true
iff vertex ``i`` receives colour ``c`` (with ``c`` in {0,1,2}).  The SAT formula
contains three families of clauses:

1. **Exactly‑one‑colour per vertex** – at least one colour:
   ``(x_{i,0} ∨ x_{i,1} ∨ x_{i,2})``
   and at most one colour (pairwise mutual exclusion): for each pair ``c < d``
   ``(¬x_{i,c} ∨ ¬x_{i,d})``.

2. **Adjacent vertices differ** – for every edge ``(u, v)`` and every colour ``c``
   we add ``(¬x_{u,c} ∨ ¬x_{v,c})``.

If the original graph is 3‑colourable, the constructed CNF is satisfiable and
conversely.  The construction uses ``3n`` variables and a number of clauses that
is polynomial in ``n`` and the number of edges, satisfying the required
complexity.

The ``reduce`` function below implements this transformation.  It does **not**
invoke any solver; it merely builds the SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  The format follows the docstring of the
        ``ThreeColoring`` class in ``problems.py``.

    Returns
    -------
    dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"`` as required
        by the ``Sat`` class.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Each vertex gets three variables: one for each colour.
    # Variable numbering starts at 1, so variable for vertex i, colour c is:
    #   var = i * 3 + c + 1
    num_vars = n * 3
    clauses: List[List[int]] = []

    # 1. At least one colour per vertex.
    for i in range(n):
        clause = [i * 3 + 1, i * 3 + 2, i * 3 + 3]
        clauses.append(clause)

        # 2. At most one colour: pairwise exclusions.
        # (¬x_i0 ∨ ¬x_i1), (¬x_i0 ∨ ¬x_i2), (¬x_i1 ∨ ¬x_i2)
        clauses.append([-(i * 3 + 1), -(i * 3 + 2)])
        clauses.append([-(i * 3 + 1), -(i * 3 + 3)])
        clauses.append([-(i * 3 + 2), -(i * 3 + 3)])

    # 3. Edge constraints: adjacent vertices cannot share a colour.
    for u, v in edges:
        # Defensive: ensure vertices are within range (the validator will catch
        # malformed inputs, but we keep the code robust).
        if not (0 <= u < n and 0 <= v < n):
            continue
        for c in range(3):
            var_u = u * 3 + c + 1
            var_v = v * 3 + c + 1
            clauses.append([ -var_u, -var_v ])

    return {"num_vars": num_vars, "clauses": clauses}


# The module can be executed directly for a quick sanity test, but this is
# optional and does not affect the reduction functionality required by the
# evaluation harness.
if __name__ == "__main__":
    import json, sys
    if len(sys.argv) != 2:
        print("Usage: python reduce.py <input_json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        inp = json.load(f)
    out = reduce(inp)
    json.dump(out, sys.stdout, separators=(",", ":"))
