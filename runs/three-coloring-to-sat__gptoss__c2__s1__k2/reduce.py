"""Reduction from 3-Coloring to SAT.

The source problem is defined in ``problems.py`` as ``ThreeColoring`` with
instances of the form ``{"n": n, "edges": [[u, v], ...]}``.  The target problem
is ``Sat`` with instances ``{"num_vars": m, "clauses": [[literal, ...], ...]}``
where literals are integers ``+v`` (positive) or ``-v`` (negative) and variables
are numbered from ``1`` to ``m``.

For each vertex ``v`` we introduce three Boolean variables indicating whether
``v`` receives colour 0, 1 or 2.  Variable ``id(v, c)`` is mapped to the integer
``v * 3 + c + 1`` (so the IDs start at 1).  The reduction adds the standard
3‑colouring constraints in conjunctive normal form:

1. **Each vertex receives at least one colour** – a clause ``[id(v,0),
   id(v,1), id(v,2)]``.
2. **Each vertex receives at most one colour** – for every unordered pair of
   colours ``c1 < c2`` we add ``[-id(v,c1), -id(v,c2)]``.
3. **Adjacent vertices cannot share a colour** – for every edge ``(u, v)`` and
   every colour ``c`` we add ``[-id(u,c), -id(v,c)]``.

The construction uses ``m = n * 3`` variables and a number of clauses that is
polynomial in ``n`` and the number of edges, satisfying the required
polynomial‑time bound.

The function ``reduce`` takes a 3‑colouring instance and returns a SAT instance
in the format expected by the ``Sat`` class.
"""

from typing import List, Dict, Any


def _var_id(v: int, colour: int) -> int:
    """Return the SAT variable number for vertex ``v`` and colour ``colour``.

    Variables are numbered from 1.  ``colour`` must be 0, 1 or 2.
    """
    return v * 3 + colour + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  Vertices are numbered ``0`` … ``n-1``.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` such that the
        SAT instance is satisfiable iff the original graph is 3‑colourable.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Number of SAT variables: three per vertex.
    m = n * 3
    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clause = [_var_id(v, 0), _var_id(v, 1), _var_id(v, 2)]
        clauses.append(clause)

        # 2. Each vertex gets at most one colour (pairwise mutual exclusion).
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_id(v, c1), -_var_id(v, c2)])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        # The problem statement guarantees u != v and no duplicate edges.
        for c in range(3):
            clauses.append([-_var_id(u, c), -_var_id(v, c)])

    return {"num_vars": m, "clauses": clauses}

