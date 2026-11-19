"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...]}

where ``n`` is the number of vertices (labeled ``0 .. n-1``) and ``edges``
is a list of undirected edges.  The target problem (ThreeSat) expects an
instance of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer: a positive ``v`` means variable ``v``
is true, a negative ``-v`` means variable ``v`` is false.  Every clause must
contain exactly three *different* variables.

The classic reduction creates three Boolean variables per vertex to
represent its colour.  Binary constraints ("at most one colour" and
"adjacent vertices cannot share a colour") are turned into 3‑CNF using a
fresh auxiliary variable ``y``:

    (¬a ∨ ¬b)  ⇝  (¬a ∨ ¬b ∨  y) ∧ (¬a ∨ ¬b ∨ ¬y)

Both clauses are satisfied iff ``¬a ∨ ¬b`` holds, because if ``a`` and ``b``
were true the two clauses would force ``y`` to be simultaneously true and
false.

The reduction runs in polynomial time and yields a formula that is
satisfiable exactly when the input graph is 3‑colourable.
"""

from __future__ import annotations

from typing import Dict, List


def _var_index(vertex: int, colour: int) -> int:
    """Return the 1‑based variable index for ``vertex`` coloured ``colour``.

    ``colour`` ∈ {0,1,2}.  Variables are numbered consecutively: vertex 0
    uses 1,2,3; vertex 1 uses 4,5,6; etc.
    """
    return vertex * 3 + colour + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance: dict with keys ``"n"`` and ``"edges"``.

    Returns
    -------
    dict: ``{"num_vars": m, "clauses": [...]}`` suitable for the ThreeSat
    solver.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Empty graph -> trivially satisfiable empty CNF.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    clauses: List[List[int]] = []
    # First fresh auxiliary variable after the colour variables.
    next_var: int = n * 3 + 1

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([_var_index(v, 0), _var_index(v, 1), _var_index(v, 2)])

    # Helper to encode (¬a ∨ ¬b) using a fresh auxiliary variable.
    def add_not_a_or_not_b(a: int, b: int) -> None:
        nonlocal next_var
        aux = next_var
        next_var += 1
        clauses.append([-a, -b, aux])
        clauses.append([-a, -b, -aux])

    # 2. At most one colour per vertex.
    for v in range(n):
        for c1, c2 in ((0, 1), (0, 2), (1, 2)):
            a = _var_index(v, c1)
            b = _var_index(v, c2)
            add_not_a_or_not_b(a, b)

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        for colour in (0, 1, 2):
            a = _var_index(u, colour)
            b = _var_index(v, colour)
            add_not_a_or_not_b(a, b)

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}


__all__ = ["reduce"]
