"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`Sat` defined in the same file.

For each vertex ``v`` (0‑based) we introduce three Boolean variables
``X_{v,0}``, ``X_{v,1}``, ``X_{v,2}`` representing that the vertex is
colored with colour 0, 1 or 2 respectively.  Variables are numbered
sequentially starting at 1 as required by the SAT format:

    var_id(v, c) = v * 3 + c + 1

Constraints encoded as CNF clauses:

1. **Exactly one colour per vertex**
   * At least one colour:   ``X_{v,0} ∨ X_{v,1} ∨ X_{v,2}``
   * At most one colour: for each pair of distinct colours ``c1 < c2``
     ``¬X_{v,c1} ∨ ¬X_{v,c2}``

2. **Adjacent vertices must differ**
   For each edge (u, v) and each colour c:
   ``¬X_{u,c} ∨ ¬X_{v,c}``

The construction is polynomial in the size of the graph (O(n + |E|)).
Edge cases are handled automatically: an empty graph yields a SAT
instance with zero variables and zero clauses, which is trivially
 satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def _var_id(v: int, colour: int) -> int:
    """Return the SAT variable number for vertex *v* and colour *colour*.

    Variables are numbered from 1 upwards as required by the SAT format.
    """
    return v * 3 + colour + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the :class:`ThreeColoring` format.

    Returns
    -------
    dict
        A dictionary adhering to the :class:`Sat` format such that the
        SAT instance is satisfiable iff the original graph is 3‑colorable.
    """
    # Validate the source instance – will raise InvalidInstance on error.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []

    # 1. Exactly one colour per vertex.
    for v in range(n):
        # At least one colour.
        clause = [_var_id(v, c) for c in range(3)]
        clauses.append(clause)
        # At most one colour – pairwise negative clauses.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_id(v, c1), -_var_id(v, c2)])

    # 2. Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var_id(u, c), -_var_id(v, c)])

    sat_instance: Dict = {
        "num_vars": n * 3,
        "clauses": clauses,
    }

    # Validate the produced SAT instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

