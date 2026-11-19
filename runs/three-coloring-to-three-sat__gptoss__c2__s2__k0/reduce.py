"""Reduction from 3‑Coloring to 3‑SAT.

The source problem (``ThreeColoring``) expects an instance of the form::

    {"n": <number of vertices>, "edges": [[u, v], ...]}

The target problem (``ThreeSat``) expects an instance of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is a signed integer ``+v`` (meaning variable ``v``
is true) or ``-v`` (meaning variable ``v`` is false).  Every clause must
contain exactly three *distinct* variables, and a clause may not contain a
variable together with its negation.

The classic reduction introduces three Boolean variables per vertex –
``x_{i,1}``, ``x_{i,2}``, ``x_{i,3}`` – indicating which colour the vertex
receives.  The constraints are:

1. **Each vertex receives at least one colour** – a single 3‑literal clause
   ``(x_{i,1} ∨ x_{i,2} ∨ x_{i,3})``.
2. **Each vertex receives at most one colour** – for every unordered pair of
   colours ``c1 < c2`` we need ``(¬x_{i,c1} ∨ ¬x_{i,c2})``.
3. **Adjacent vertices receive different colours** – for every edge ``(u, v)``
   and colour ``c`` we need ``(¬x_{u,c} ∨ ¬x_{v,c})``.

Constraints (2) and (3) are 2‑literal clauses, but the target language only
allows clauses of size three.  A standard trick is to replace a clause
``(a ∨ b)`` by the pair of clauses ``(a ∨ b ∨ y)`` and ``(a ∨ b ∨ ¬y)`` where
``y`` is a fresh auxiliary variable that appears only in this pair.  The two
clauses together are equivalent to the original 2‑literal clause because they
cannot both be satisfied unless ``a ∨ b`` holds.

Using this transformation we obtain a 3‑CNF formula that is satisfiable iff the
input graph is 3‑colourable.  The construction is polynomial in the size of the
graph.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``ThreeColoring`` instance to a ``ThreeSat`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of ``[u, v]``).

    Returns
    -------
    dict
        A ``ThreeSat`` instance respecting the exact format required by
        ``problems.py``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Helper to map (vertex, colour) -> variable id (1‑based as required).
    def var_id(vertex: int, colour: int) -> int:
        # colour is in {1,2,3}
        return vertex * 3 + colour

    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var_id(v, 1), var_id(v, 2), var_id(v, 3)])

    # The next fresh variable id after the base colour variables.
    next_aux: int = 3 * n + 1

    # Helper to replace a 2‑literal clause (a ∨ b) with two 3‑literal clauses
    # using a fresh auxiliary variable.
    def add_2lit_clause(lit1: int, lit2: int) -> None:
        nonlocal next_aux
        aux = next_aux
        next_aux += 1
        # (lit1 ∨ lit2 ∨  aux) and (lit1 ∨ lit2 ∨ -aux)
        clauses.append([lit1, lit2, aux])
        clauses.append([lit1, lit2, -aux])

    # 2. At most one colour per vertex (pairwise not‑both constraints).
    for v in range(n):
        # generate pairs (1,2), (1,3), (2,3)
        add_2lit_clause(-var_id(v, 1), -var_id(v, 2))
        add_2lit_clause(-var_id(v, 1), -var_id(v, 3))
        add_2lit_clause(-var_id(v, 2), -var_id(v, 3))

    # 3. Different colours for adjacent vertices.
    for u, v in edges:
        for c in (1, 2, 3):
            add_2lit_clause(-var_id(u, c), -var_id(v, c))

    num_vars = next_aux - 1
    return {"num_vars": num_vars, "clauses": clauses}

