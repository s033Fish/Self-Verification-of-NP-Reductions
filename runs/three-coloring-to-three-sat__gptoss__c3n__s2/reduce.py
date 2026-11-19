"""Reduction from 3-Coloring to 3-SAT.

The reduction follows the classic construction:

* For each vertex ``v`` and each colour ``c`` in {0,1,2} we introduce a
  Boolean variable ``X_{v,c}`` meaning *vertex v receives colour c*.
* For each vertex we add a clause forcing it to receive **at least one**
  colour: ``X_{v,0} ∨ X_{v,1} ∨ X_{v,2}``.
* To enforce **at most one** colour per vertex we add, for every unordered
  pair of colours ``c1 < c2``, the constraint ``¬X_{v,c1} ∨ ¬X_{v,c2}``.
  3‑SAT clauses must contain exactly three literals, therefore we pad each
  2‑literal clause with an auxiliary variable ``Z`` and also with its
  negation.  The pair of clauses ``(¬X ∨ ¬Y ∨ Z)`` and ``(¬X ∨ ¬Y ∨ ¬Z)``
  together are equivalent to the original 2‑literal clause.
* For each edge ``(u, v)`` and each colour ``c`` we add the constraint that
  the endpoints cannot share the same colour: ``¬X_{u,c} ∨ ¬X_{v,c}``.
  This is padded in the same way with ``Z``.

All generated clauses have exactly three *different* variables, never a
variable together with its negation, satisfying the ``ThreeSat`` format.

The reduction runs in polynomial time: the number of variables is
``3·n + 1`` and the number of clauses is ``O(n + n·C(3,2) + |E|·3)`` which is
quadratic in the size of the input graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, ThreeSat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a ``ThreeColoring`` instance as defined
        in ``problems.py``.

    Returns
    -------
    dict
        A ``ThreeSat`` instance that is satisfiable iff the original graph
        is 3‑colorable.
    """
    # Validate the source instance.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: empty graph – trivially 3‑colorable.  An empty CNF is always
    # satisfiable, regardless of the number of variables.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Mapping: vertex v (0‑based) and colour c (0,1,2) -> variable index (1‑based)
    def var(v: int, c: int) -> int:
        return v * 3 + c + 1

    aux_var = 3 * n + 1  # the auxiliary variable Z used for padding
    num_vars = aux_var
    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. Each vertex receives at most one colour (pairwise exclusion).
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                a = -var(v, c1)
                b = -var(v, c2)
                # Pad with Z and ¬Z to obtain two 3‑literal clauses.
                clauses.append([a, b, aux_var])
                clauses.append([a, b, -aux_var])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for c in range(3):
            a = -var(u, c)
            b = -var(v, c)
            clauses.append([a, b, aux_var])
            clauses.append([a, b, -aux_var])

    # Validate the target instance before returning.
    ThreeSat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

