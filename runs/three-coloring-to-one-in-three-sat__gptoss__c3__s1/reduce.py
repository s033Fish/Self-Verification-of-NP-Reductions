"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is ``ThreeColoring`` defined in ``problems.py``.  An
instance is a dict ``{"n": n, "edges": [[u, v], ...]}`` describing a simple
undirected graph on vertices ``0..n-1``.

The target problem is ``OneInThreeSat``.  An instance is a dict ``{"num_vars":
+m, "clauses": [[a, b, c], ...]}`` where each clause contains three *distinct*
variables (positive integers) and must be satisfied by an assignment that
+makes **exactly one** of the three literals true.

The classic polynomial‑time reduction works as follows.

* For each vertex ``v`` we introduce three Boolean variables ``v_0, v_1, v_2``
  representing that ``v`` receives colour ``0, 1, 2`` respectively.
* A clause ``[v_0, v_1, v_2]`` forces exactly one of the three colours to be
  chosen – this is precisely the vertex‑colour constraint.
* For each edge ``(u, v)`` and each colour ``c`` we introduce a fresh auxiliary
  variable ``t_{u,v,c}`` and add the clause ``[u_c, v_c, t_{u,v,c}]``.
  The clause is satisfied iff **not both** ``u_c`` and ``v_c`` are true:
  - If both are true the clause would have at least two true literals – not
    allowed.
  - If exactly one of ``u_c`` or ``v_c`` is true we set the auxiliary to
    false, giving exactly one true literal.
  - If both are false we set the auxiliary to true, again giving exactly one
    true literal.
  Hence the auxiliary variable can always be chosen to satisfy the clause
  unless the two endpoint vertices share the same colour, which is exactly the
  edge‑colour restriction.

The construction uses ``3n`` vertex variables and ``3|E|`` auxiliary variables,
so the total number of variables is ``m = 3n + 3|E|`` – polynomial in the size
of the graph.

The ``reduce`` function validates the input, builds the mapping from logical
variables to concrete integer identifiers (starting at 1, as required by the
target format) and returns a well‑formed 1‑in‑3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# Import the problem classes for validation (they raise ``InvalidInstance`` on
# malformed input).  The import is cheap and works in the execution environment
# used for the tests.
from problems import ThreeColoring, OneInThreeSat


def reduce(instance: dict) -> dict:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeColoring`` specification.

    Returns
    -------
    dict
        A dictionary adhering to the ``OneInThreeSat`` specification such that
        the original graph is 3‑colourable iff the produced formula is
        satisfiable under the *exactly‑one* semantics.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong, matching the contract of the reduction function.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping from our logical variables to concrete integer IDs.
    var_id: Dict[Tuple[int, int] | Tuple[str, int, int, int], int] = {}
    next_id = 1

    # Vertex colour variables: (v, colour) -> id
    for v in range(n):
        for c in range(3):
            var_id[(v, c)] = next_id
            next_id += 1

    # Auxiliary variables for edge‑colour constraints: ("t", u, v, c) -> id
    for u, v in edges:
        for c in range(3):
            var_id[("t", u, v, c)] = next_id
            next_id += 1

    num_vars = next_id - 1
    clauses: List[List[int]] = []

    # Vertex clauses – exactly one colour per vertex.
    for v in range(n):
        clauses.append([var_id[(v, 0)], var_id[(v, 1)], var_id[(v, 2)]])

    # Edge clauses – forbid both endpoints sharing the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append(
                [var_id[(u, c)], var_id[(v, c)], var_id[("t", u, v, c)]]
            )

    # The target format expects exactly the keys shown below.
    return {"num_vars": num_vars, "clauses": clauses}

