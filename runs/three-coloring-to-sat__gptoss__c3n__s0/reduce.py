"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`Sat` defined in the same file.

For a graph with ``n`` vertices we create three Boolean variables per
vertex, encoding the colour chosen for that vertex.  Variable numbers
are assigned as follows::

    var(i, c) = 3*i + c + 1   # i = vertex index (0‑based), c = colour (0,1,2)

The SAT formula consists of three families of clauses:

* **At least one colour** for each vertex ``i``::

      (v_i0 ∨ v_i1 ∨ v_i2)

* **At most one colour** for each vertex – for every unordered pair of
  colours ``c1 < c2``::

      (¬v_ic1 ∨ ¬v_ic2)

* **Edge constraints** – for each edge ``[u, v]`` and each colour ``c``::

      (¬v_uc ∨ ¬v_vc)

These clauses exactly enforce a proper 3‑colouring.  The construction
uses ``3*n`` variables and a number of clauses polynomial in ``n`` and the
number of edges, satisfying the required polynomial‑time reduction.

The ``reduce`` function validates the input using the ``ThreeColoring``
class and returns a dictionary compatible with the ``Sat`` class.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def _var(vertex: int, colour: int) -> int:
    """Return the SAT variable index for ``vertex`` with colour ``colour``.

    Variables are 1‑based as required by the SAT definition.
    ``colour`` must be 0, 1 or 2.
    """
    return 3 * vertex + colour + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described in the docstring of
        :class:`ThreeColoring` (keys ``"n"`` and ``"edges"``).

    Returns
    -------
    dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"``.
    """
    # Validate the source instance first – this will raise InvalidInstance on
    # malformed input.
    ThreeColoring.validate(instance)

    n: int = instance["n"]  # number of vertices
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clause = [_var(v, c) for c in range(3)]
        clauses.append(clause)

    # 2. Each vertex receives at most one colour (pairwise mutual exclusion).
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var(v, c1), -_var(v, c2)])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    sat_instance = {"num_vars": 3 * n, "clauses": clauses}
    # Validate the produced SAT instance before returning.
    Sat.validate(sat_instance)
    return sat_instance
