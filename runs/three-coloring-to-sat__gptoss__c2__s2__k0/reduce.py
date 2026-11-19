"""Reduction from 3-Coloring to SAT.

The source problem is defined by the ``ThreeColoring`` class in ``problems.py``
and expects instances of the form ``{"n": n, "edges": [[u, v], ...]}``.
The target problem is SAT, represented by a dictionary ``{"num_vars": m,
"clauses": [[literal, ...], ...]}`` where literals are signed integers.

For each vertex we introduce three Boolean variables indicating whether the
vertex receives colour 0, 1 or 2.  The reduction adds the standard constraints:

* **Exactly one colour per vertex** – encoded as one clause requiring at
  least one colour and three pairwise‑negative clauses forbidding two colours
  simultaneously.
* **Adjacent vertices must differ** – for every edge and every colour we add a
  clause that forbids both endpoints from taking that colour.

The construction is polynomial in the size of the graph (``O(n + |E|)``) and
preserves satisfiability: a proper 3‑colouring yields a satisfying assignment
to the SAT instance and vice‑versa.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the source problem class only for validation; the reduction itself
# does not depend on any of its methods beyond the instance format.
from problems import ThreeColoring


def _var_index(vertex: int, colour: int) -> int:
    """Return the SAT variable number for ``vertex`` with ``colour``.

    Variables are numbered starting at 1.  For vertex ``v`` (0‑based) and colour
    ``c`` in ``{0,1,2}`` we use ``v * 3 + c + 1``.  This yields exactly ``3*n``
    variables for a graph with ``n`` vertices.
    """
    return vertex * 3 + colour + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as described in the
        docstring of :class:`ThreeColoring`.

    Returns
    -------
    dict
        A SAT instance in the format required by the ``Sat`` problem class.
    """
    # Validate the input using the source problem's validator to catch
    # malformed instances early.  This call will raise ``InvalidInstance`` if
    # the format is wrong, matching the expected behaviour of the benchmark.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clause = [_var_index(v, c) for c in range(3)]
        clauses.append(clause)

    # 2. Each vertex receives at most one colour (pairwise exclusion).
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_index(v, c1), -_var_index(v, c2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var_index(u, c), -_var_index(v, c)])

    num_vars = 3 * n
    return {"num_vars": num_vars, "clauses": clauses}

