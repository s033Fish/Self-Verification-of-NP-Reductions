"""Reduction from 3-Coloring to 3-SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability) and the
target is :class:`ThreeSat` (3‑SAT).  Both classes are defined in ``problems.py``
and provide a ``validate`` method for their respective instance formats.

The reduction constructs a Boolean formula that is satisfiable iff the input
graph can be coloured with three colours.  For each vertex ``v`` and colour
``c`` (0, 1, 2) we introduce a Boolean variable ``X_{v,c}`` meaning *v receives
colour c*.  The constraints are:

1. **Exactly one colour per vertex** – encoded as
   *at‑least‑one* clause ``(X_{v,0} ∨ X_{v,1} ∨ X_{v,2})`` and three
   *at‑most‑one* clauses ``(¬X_{v,i} ∨ ¬X_{v,j})`` for each pair of colours.
   Since the target problem requires clauses of *exactly three literals on
   three distinct variables*, each 2‑literal clause is padded with an auxiliary
   variable ``Y`` that appears in two complementary clauses:
   ``(¬X_{v,i} ∨ ¬X_{v,j} ∨ Y)`` and ``(¬X_{v,i} ∨ ¬X_{v,j} ∨ ¬Y)``.  The pair
   forces the original disjunction regardless of the value of ``Y``.

2. **Adjacency constraint** – for each edge ``(u, v)`` and each colour ``c`` we
   must forbid both endpoints having the same colour.  This is encoded by the
   clause ``(¬X_{u,c} ∨ ¬X_{v,c})`` padded in the same way with a fresh
   auxiliary variable.

The construction uses a fresh auxiliary variable for every padded clause.
All clauses contain three distinct variables, satisfying the strict format of
``ThreeSat``.

The ``reduce`` function validates the source instance, builds the clause list,
and returns a dictionary compatible with ``ThreeSat.validate``.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeColoring, ThreeSat


def _new_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a one‑element list holding the current maximum variable
    number.  Using a list allows us to modify it in‑place.
    """
    counter[0] += 1
    return counter[0]


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeColoring`.

    Returns
    -------
    dict
        A dictionary adhering to the format of :class:`ThreeSat`.
    """
    # Validate source instance first.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Primary variables: X_{v,c} -> index = v*3 + c + 1 (variables are 1‑based).
    def var(v: int, c: int) -> int:
        return v * 3 + c + 1

    # Keep track of the highest variable index used so far.
    max_var = n * 3
    var_counter = [max_var]

    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Helper to add a padded 2‑literal clause (a ∨ b) using a fresh aux variable.
    def add_padded_or(lit1: int, lit2: int) -> None:
        aux = _new_var(var_counter)
        # (lit1 ∨ lit2 ∨ aux) and (lit1 ∨ lit2 ∨ -aux)
        clauses.append([lit1, lit2, aux])
        clauses.append([lit1, lit2, -aux])

    # 2. Each vertex gets at most one colour (pairwise constraints).
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                # ¬X_{v,c1} ∨ ¬X_{v,c2}
                add_padded_or(-var(v, c1), -var(v, c2))

    # 3. Edge constraints: adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in range(3):
            add_padded_or(-var(u, c), -var(v, c))

    # Build the final instance.
    result = {"num_vars": var_counter[0], "clauses": clauses}
    # Validate target instance before returning.
    ThreeSat.validate(result)
    return result

