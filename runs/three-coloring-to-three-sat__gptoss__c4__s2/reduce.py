"""Reduction from 3-Coloring to 3-SAT.

The reduction follows the classic textbook construction:

* For each vertex ``v`` we create three Boolean variables
  ``x_{v,1}``, ``x_{v,2}``, ``x_{v,3}`` meaning that ``v`` receives colour
  1, 2 or 3 respectively.
* Every vertex must receive **at least one** colour – a single 3‑literal
  clause ``(x_{v,1} ∨ x_{v,2} ∨ x_{v,3})``.
* Every vertex must receive **at most one** colour.  For each unordered
  pair of colours ``(i, j)`` we need the clause ``(¬x_{v,i} ∨ ¬x_{v,j})``.
  Since the target problem requires *exactly* three literals per clause,
  we introduce a fresh dummy variable ``d`` and replace the 2‑literal clause
  by the pair ``(¬x_{v,i} ∨ ¬x_{v,j} ∨  d)`` and ``(¬x_{v,i} ∨ ¬x_{v,j} ∨ ¬d)``.
  The two clauses together are equivalent to the original 2‑literal clause.
* For each edge ``(u, v)`` and each colour ``c`` we must forbid the two
  endpoints from sharing that colour, i.e. ``(¬x_{u,c} ∨ ¬x_{v,c})``.
  We encode it with the same dummy‑variable trick.

The construction runs in polynomial time and produces a 3‑CNF formula that
is satisfiable iff the original graph is 3‑colourable.

The function ``reduce`` validates the input using ``ThreeColoring.validate``
and returns a dictionary that conforms to the ``ThreeSat`` instance format.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeColoring, ThreeSat, InvalidInstance


def _add_two_literal_clause(clauses: List[List[int]], a: int, b: int, next_var: int) -> int:
    """Encode the 2‑literal clause ``(a ∨ b)`` using a fresh dummy variable.

    ``a`` and ``b`` are integer literals (positive for true, negative for false).
    ``next_var`` is the identifier of a fresh variable that has not been used
    yet.  The function appends the two required 3‑literal clauses to ``clauses``
    and returns the next unused variable identifier.
    """
    d = next_var
    # (a ∨ b ∨ d) and (a ∨ b ∨ -d) together enforce (a ∨ b)
    clauses.append([a, b, d])
    clauses.append([a, b, -d])
    return next_var + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance: dict
        Must follow the format of :class:`ThreeColoring` – ``{"n": int,
        "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.
    """
    # Validate input according to the source problem definition.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: empty graph – trivially satisfiable with 0 variables.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    clauses: List[List[int]] = []
    # Map (vertex, colour) -> variable id. Colours are 1,2,3.
    var_id = lambda v, c: v * 3 + c  # 1‑based variable numbers
    next_var = n * 3 + 1  # first fresh dummy variable

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var_id(v, 1), var_id(v, 2), var_id(v, 3)])

    # 2. Each vertex gets at most one colour (pairwise constraints).
    for v in range(n):
        for c1 in (1, 2, 3):
            for c2 in (c1 + 1, 4):  # generate pairs (1,2), (1,3), (2,3)
                if c2 > 3:
                    continue
                a = -var_id(v, c1)
                b = -var_id(v, c2)
                next_var = _add_two_literal_clause(clauses, a, b, next_var)

    # 3. Edge constraints – adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in (1, 2, 3):
            a = -var_id(u, c)
            b = -var_id(v, c)
            next_var = _add_two_literal_clause(clauses, a, b, next_var)

    num_vars = next_var - 1
    # Validate the produced instance against the target definition.
    ThreeSat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

