"""Reduction from 3-Coloring to 3-SAT.

The source problem is defined in :class:`problems.ThreeColoring` and the
target in :class:`problems.ThreeSat`.  Both classes only provide a
``validate`` method – there are no solvers.  This file implements a
polynomial‑time many‑one reduction that can be used to transform any
instance of 3‑Coloring into an equivalent instance of 3‑SAT.

The classic reduction introduces, for every vertex ``v`` and colour
``c ∈ {0,1,2}``, a Boolean variable ``x_{v,c}`` that is true iff ``v``
receives colour ``c``.  The constraints are:

* **Exactly one colour per vertex** – we encode this as
  *at‑least‑one* (a 3‑literal clause) and three *at‑most‑one* clauses
  (pairwise negations).  The at‑most‑one clauses are binary; they are
  padded to size three using an auxiliary variable ``y`` as follows:
  ``(¬a ∨ ¬b)`` becomes ``(¬a ∨ ¬b ∨ y) ∧ (¬a ∨ ¬b ∨ ¬y)``.  This
  transformation preserves satisfiability and respects the 3‑SAT
  format (exactly three literals on three distinct variables, no
  literal appears both positively and negatively).

* **Edge constraints** – for each edge ``(u, v)`` and each colour ``c``
  we forbid both endpoints from sharing the colour: ``(¬x_{u,c} ∨ ¬x_{v,c})``.
  These binary clauses are padded in the same way as above.

The reduction runs in polynomial time: the number of variables is
``3·n + 1`` (the extra variable is the shared padding variable) and the
number of clauses is linear in the size of the input graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, ThreeSat


def _add_padded_binary_clause(
    clauses: List[List[int]], a: int, b: int, aux: int
) -> None:
    """Add a 3‑SAT encoding of the binary clause ``(a ∨ b)``.

    The pair ``(a ∨ b ∨ aux)`` and ``(a ∨ b ∨ ¬aux)`` is equivalent to
    ``(a ∨ b)`` regardless of ``aux``'s value.  Using a single shared
    auxiliary variable keeps the variable count linear.
    """
    clauses.append([a, b, aux])
    clauses.append([a, b, -aux])


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the format of ``ThreeColoring`` –
        ``{"n": int, "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
        that is satisfiable iff the input graph is 3‑colorable.
    """
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    def var(i: int, c: int) -> int:
        return i * 3 + c + 1

    clauses: List[List[int]] = []
    # One auxiliary variable for all padding
    aux = 3 * n + 1

    # 1. At‑least‑one colour per vertex
    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    # 2. At‑most‑one colour per vertex (pairwise negations)
    for i in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                a = -var(i, c1)
                b = -var(i, c2)
                _add_padded_binary_clause(clauses, a, b, aux)

    # 3. Edge constraints
    for u, v in edges:
        for c in range(3):
            a = -var(u, c)
            b = -var(v, c)
            _add_padded_binary_clause(clauses, a, b, aux)

    num_vars = aux
    ThreeSat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

