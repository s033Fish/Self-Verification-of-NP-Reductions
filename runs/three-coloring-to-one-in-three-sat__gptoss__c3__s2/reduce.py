"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability) and the
target problem is :class:`OneInThreeSat`.  Instances are plain dictionaries as
described in ``problems.py``.

The classic polynomial‑time reduction works as follows.

* For each vertex *v* we introduce three Boolean variables
  ``v_R``, ``v_G`` and ``v_B`` meaning that *v* receives the colour red,
  green or blue respectively.
* A clause ``[v_R, v_G, v_B]`` is added.  In 1‑in‑3‑SAT a clause forces **exactly
  one** of its three literals to be true, therefore this clause guarantees
  that each vertex receives *exactly one* colour.
* For each edge ``(u, v)`` and for each colour ``c`` we introduce a fresh
  auxiliary variable ``w_{u,v,c}``.  The clause ``[u_c, v_c, w_{u,v,c}]``
  forces exactly one of the three literals to be true.  Consequently ``u_c``
  and ``v_c`` cannot both be true – this forbids the two adjacent vertices
  from sharing the same colour.  The auxiliary variable can be set to true
  when both ``u_c`` and ``v_c`` are false, satisfying the clause without
  affecting any other constraints.

All variables are numbered starting at ``1`` as required by the problem
specification.  The reduction runs in time linear in the size of the input
graph (``O(n + |E|)``) and produces a formula whose size is also linear.

The function ``reduce`` validates the source instance, builds the target
instance, validates it (as a sanity check) and returns it.
"""

from __future__ import annotations

from typing import List, Tuple

# Import the problem classes from the provided module.
from problems import ThreeColoring, OneInThreeSat, InvalidInstance


def _vertex_var(vertex: int, colour: int) -> int:
    """Return the variable index for ``vertex`` with colour ``colour``.

    Colours are numbered ``0, 1, 2``.  Variables are numbered consecutively
    starting at ``1``.  The mapping used is ``3*vertex + colour + 1``.
    """
    return vertex * 3 + colour + 1


def reduce(instance: dict) -> dict:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as required by :class:`ThreeColoring`.

    Returns
    -------
    dict
        An instance of :class:`OneInThreeSat` (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance – this will raise InvalidInstance on bad input.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # No vertices → trivial yes instance.
    if n == 0:
        target = {"num_vars": 0, "clauses": []}
        OneInThreeSat.validate(target)  # sanity check
        return target

    clauses: List[List[int]] = []

    # 1. Vertex colour selection clauses.
    for v in range(n):
        clauses.append([
            _vertex_var(v, 0),  # red
            _vertex_var(v, 1),  # green
            _vertex_var(v, 2),  # blue
        ])

    # 2. Edge colour conflict clauses with auxiliary variables.
    # Auxiliary variables start after the vertex variables.
    next_var = n * 3 + 1
    for (u, v) in edges:
        for colour in range(3):
            w = next_var
            next_var += 1
            clauses.append([
                _vertex_var(u, colour),
                _vertex_var(v, colour),
                w,
            ])

    num_vars = next_var - 1
    target_instance = {"num_vars": num_vars, "clauses": clauses}

    # Validate the produced target instance (helps catch programming errors).
    OneInThreeSat.validate(target_instance)
    return target_instance


if __name__ == "__main__":
    # Simple manual test when the file is executed directly.
    example = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}
    print("Source instance:", example)
    print("Is 3‑colorable?", ThreeColoring.is_yes(example))
    reduced = reduce(example)
    print("Reduced instance:", reduced)
    print("Is 1‑in‑3‑SAT yes?", OneInThreeSat.is_yes(reduced))
