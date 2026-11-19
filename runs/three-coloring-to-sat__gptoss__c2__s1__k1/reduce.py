"""Reduction from 3-Coloring to SAT.

The source problem is ``ThreeColoring`` with instances of the form::

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered ``0..n-1`` and each edge is an undirected pair.

The target problem is ``Sat`` with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered ``1..m``.  A literal is a signed integer: ``+v``
means variable ``v`` is true, ``-v`` means variable ``v`` is false.

The classic polynomial‑time reduction creates, for each vertex ``i`` and
each colour ``c`` in ``{0,1,2}``, a Boolean variable ``X_{i,c}`` that is true
iff vertex ``i`` receives colour ``c``.  The SAT formula consists of three
families of clauses:

1. **Exactly‑one‑colour per vertex** – at least one colour:
   ``X_{i,0} ∨ X_{i,1} ∨ X_{i,2}``
   and at most one colour (pairwise mutual exclusion):
   ``¬X_{i,c} ∨ ¬X_{i,d}`` for all ``c < d``.

2. **Adjacent vertices must differ** – for each edge ``(u, v)`` and each colour
   ``c`` we add ``¬X_{u,c} ∨ ¬X_{v,c}``.

The resulting formula is satisfiable exactly when the original graph is
3‑colourable.

The implementation below follows this construction directly.  It runs in
``O(n + |E|)`` time and uses ``3n`` variables.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  The format matches the ``SOURCE``
        definition in ``problems.py``.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
        The returned instance is a yes‑instance iff the input graph is
        3‑colourable.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Number of variables: one for each vertex‑colour pair.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # Helper to map (vertex, colour) to variable index (1‑based).
    def var(i: int, c: int) -> int:
        return i * 3 + c + 1  # +1 because SAT variables start at 1

    # 1. Each vertex gets at least one colour.
    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    # 2. No vertex gets two colours simultaneously (pairwise exclusion).
    for i in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(i, c1), -var(i, c2)])

    # 3. Adjacent vertices must have different colours.
    for u, v in edges:
        # Ensure vertices are within range – the validator would catch this,
        # but we keep the code robust.
        if not (0 <= u < n and 0 <= v < n):
            continue
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

