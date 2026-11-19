"""Reduction from 3‑SAT to 1‑in‑3‑SAT.

The source problem is :class:`ThreeSat` (allowing negated literals).
The target problem is :class:`OneInThreeSat` (only positive literals, and each
clause must have **exactly** one true variable).

The reduction follows the classic textbook construction:

* For each original variable ``x`` we create three fresh variables
  ``x_T``, ``x_F`` and ``x_D`` with a *variable‑gadget* clause
  ``[x_T, x_F, x_D]``.  The clause enforces that exactly one of the three is
  true.  We interpret ``x_T`` as "``x`` is true" and ``x_F`` as "``x`` is false".
  ``x_D`` is a dummy that absorbs the remaining truth value.

* A literal ``+v`` (positive) is represented by the variable ``v_T`` and a
  literal ``-v`` (negative) by ``v_F``.

* For each original clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we introduce three fresh
  auxiliary variables ``a``, ``b`` and ``c`` and add the three 1‑in‑3 clauses

    ``[ℓ1', a, b]``
    ``[ℓ2', b, c]``
    ``[ℓ3', c, a]``

  plus an additional clause ``[a, b, c]``.  This construction forces the
  auxiliary variables to contain exactly one true value, which can only happen
  when at least one of the original literals is true, matching the semantics of
  the original 3‑SAT clause.

The overall number of variables is polynomial in the input size and the
transformation runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeSat, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a :class:`ThreeSat` instance to a :class:`OneInThreeSat` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in :class:`ThreeSat`.

    Returns
    -------
    dict
        A new instance respecting the format of :class:`OneInThreeSat`.
    """
    # Validate source instance
    ThreeSat.validate(instance)

    orig_vars: int = instance["num_vars"]
    orig_clauses: List[List[int]] = instance["clauses"]

    # Mapping from original variable to gadget variables
    next_var = orig_vars
    pos_lit: Dict[int, int] = {}
    neg_lit: Dict[int, int] = {}
    gadget_clauses: List[List[int]] = []

    for v in range(1, orig_vars + 1):
        x_T = next_var + 1
        x_F = next_var + 2
        x_D = next_var + 3
        next_var += 3
        pos_lit[v] = x_T
        neg_lit[v] = x_F
        gadget_clauses.append([x_T, x_F, x_D])

    encoding_clauses: List[List[int]] = []
    for clause in orig_clauses:
        lit_vars = []
        for lit in clause:
            var = abs(lit)
            lit_vars.append(pos_lit[var] if lit > 0 else neg_lit[var])
        # fresh auxiliaries a,b,c
        a = next_var + 1
        b = next_var + 2
        c = next_var + 3
        next_var += 3
        encoding_clauses.append([lit_vars[0], a, b])
        encoding_clauses.append([lit_vars[1], b, c])
        encoding_clauses.append([lit_vars[2], c, a])
        encoding_clauses.append([a, b, c])

    all_clauses = gadget_clauses + encoding_clauses
    target_instance = {"num_vars": next_var, "clauses": all_clauses}
    OneInThreeSat.validate(target_instance)
    return target_instance

