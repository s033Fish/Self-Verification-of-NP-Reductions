"""Reduction from 3-Coloring to SAT.

The source problem is ``ThreeColoring`` (graph 3‑colorability) and the
target problem is ``Sat`` (CNF satisfiability).  Both problems are defined
in ``problems.py``.  An instance of ``ThreeColoring`` is a dictionary with
keys ``"n"`` (the number of vertices) and ``"edges"`` (a list of undirected
edges).  An instance of ``Sat`` is a dictionary with keys ``"num_vars"``
and ``"clauses"`` where each clause is a list of signed integers representing
literals (+v for true, -v for false).

The classic polynomial‑time reduction encodes, for each vertex ``v`` and each
colour ``c`` (c ∈ {0,1,2}), a Boolean variable ``X_{v,c}`` that is true iff
vertex ``v`` receives colour ``c``.  The SAT formula consists of three groups
of clauses:

1. **Each vertex receives at least one colour** – a clause ``(X_{v,0} ∨ X_{v,1} ∨ X_{v,2})``.
2. **Each vertex receives at most one colour** – for every pair of colours
   ``c1 < c2`` a clause ``(¬X_{v,c1} ∨ ¬X_{v,c2})``.
3. **Adjacent vertices receive different colours** – for each edge ``(u,v)``
   and each colour ``c`` a clause ``(¬X_{u,c} ∨ ¬X_{v,c})``.

Variables are numbered consecutively: ``var_index = v * 3 + c + 1`` (the ``+1``
shifts to the 1‑based indexing required by the SAT format).

The reduction runs in time O(n + |E|) and produces a SAT instance that is
 satisfiable exactly when the original graph is 3‑colourable.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse validation utilities.
from problems import ThreeColoring, Sat


def _var_index(v: int, colour: int) -> int:
    """Return the SAT variable number for vertex ``v`` and colour ``colour``.

    ``colour`` is expected to be 0, 1 or 2.  Variables are 1‑based as required by
    the SAT definition.
    """
    return v * 3 + colour + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a SAT instance.

    The function validates the input using ``ThreeColoring.validate`` and then
    constructs the SAT instance described in the module docstring.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is incorrect.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clause = [_var_index(v, c) for c in range(3)]
        clauses.append(clause)

        # 2. Each vertex receives at most one colour (pairwise mutual exclusion).
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_index(v, c1), -_var_index(v, c2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var_index(u, c), -_var_index(v, c)])

    # Return a SAT instance in the required format.
    return {"num_vars": num_vars, "clauses": clauses}

