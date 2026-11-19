"""Reduction from 3-Coloring to 3-SAT.

The source problem is defined in :class:`ThreeColoring` (see ``problems.py``).
The target problem is :class:`ThreeSat`.

For a graph G = (V, E) we create a 3‑SAT formula that is satisfiable iff G
admits a proper 3‑coloring.  The classic encoding uses a Boolean variable
``x_{v,c}`` meaning *vertex ``v`` receives colour ``c``* (c ∈ {1,2,3}).

Constraints:
  * **Exactly one colour per vertex** – encoded as
      - at‑least‑one clause ``(x_{v,1} ∨ x_{v,2} ∨ x_{v,3})``
      - at‑most‑one clauses ``(¬x_{v,i} ∨ ¬x_{v,j})`` for each pair i<j.
    The at‑most‑one clauses are 2‑literal, but the target format requires
    exactly three literals per clause.  We transform a 2‑literal clause
    ``(a ∨ b)`` into two 3‑literal clauses using a fresh auxiliary variable
    ``y``:
        (a ∨ b ∨ y) ∧ (a ∨ b ∨ ¬y)
    This construction is logically equivalent because both new clauses are
    satisfied iff the original clause is satisfied.
  * **Adjacency constraint** – for each edge (u, v) and each colour c we
    forbid both endpoints from taking the same colour:
        (¬x_{u,c} ∨ ¬x_{v,c})
    The same 2‑to‑3 literal transformation is applied.

All clauses produced contain three *different* variables and never contain
both a variable and its negation, satisfying the strict 3‑SAT format.

The reduction runs in polynomial time: O(|V| + |E|) variables and O(|V| + |E|)
clauses.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeColoring, ThreeSat


def _new_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a one‑element list so that it can be mutated inside the
    helper without using the ``nonlocal`` keyword (which would require a
    nested function).  The first variable returned is 1.
    """
    counter[0] += 1
    return counter[0]


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described in ``ThreeColoring``.

    Returns
    -------
    dict
        A dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
        satisfying the validation rules of :class:`ThreeSat`.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping (vertex, colour) -> variable number.
    # Colours are 1,2,3.
    var_map: Dict[Tuple[int, int], int] = {}
    counter = [0]  # mutable counter for fresh variable numbers
    for v in range(n):
        for c in (1, 2, 3):
            var_map[(v, c)] = _new_var(counter)

    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([
            var_map[(v, 1)],
            var_map[(v, 2)],
            var_map[(v, 3)],
        ])

    # Helper to encode a 2‑literal clause (a ∨ b) as two 3‑literal clauses
    # using a fresh auxiliary variable y.
    def encode_two_literal(a: int, b: int) -> None:
        y = _new_var(counter)
        # (a ∨ b ∨ y) and (a ∨ b ∨ -y)
        clauses.append([a, b, y])
        clauses.append([a, b, -y])

    # 2. At most one colour per vertex.
    for v in range(n):
        # pairs (1,2), (1,3), (2,3)
        pairs = [(1, 2), (1, 3), (2, 3)]
        for c1, c2 in pairs:
            a = -var_map[(v, c1)]
            b = -var_map[(v, c2)]
            encode_two_literal(a, b)

    # 3. Edge constraints: adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in (1, 2, 3):
            a = -var_map[(u, c)]
            b = -var_map[(v, c)]
            encode_two_literal(a, b)

    num_vars = counter[0]
    result = {"num_vars": num_vars, "clauses": clauses}
    # Validate the target instance before returning.
    ThreeSat.validate(result)
    return result

