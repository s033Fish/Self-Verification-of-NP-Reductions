"""Reduction from SAT to 3‑SAT.

The source problem is :class:`Sat` defined in ``problems.py``.  An instance
is a dictionary ``{"num_vars": m, "clauses": [[l, ...], ...]}`` where each
clause may contain an arbitrary number of literals (including the empty
clause).  The target problem is :class:`ThreeSat` – a 3‑CNF formula where each
clause has exactly three *distinct* variables and does not contain a variable
and its negation.

The reduction follows the textbook construction:

* An empty clause makes the formula unsatisfiable.  We return a fixed
  unsatisfiable 3‑SAT instance (see ``_UNSAT_CORE`` below).
* A clause of length 1 ``(l)`` is replaced by the four 3‑clauses
  ``(l ∨ a ∨ b), (l ∨ a ∨ ¬b), (l ∨ ¬a ∨ b), (l ∨ ¬a ∨ ¬b)`` where ``a``
  and ``b`` are fresh variables.  The four clauses are jointly equivalent to
  the original unit clause.
* A clause of length 2 ``(l1, l2)`` is replaced by the two 3‑clauses
  ``(l1 ∨ l2 ∨ a)`` and ``(l1 ∨ l2 ∨ ¬a)`` with a fresh variable ``a``.
* A clause of length ≥3 is broken into a chain of 3‑clauses using fresh
  auxiliary variables ``y_i`` as described in many textbooks.

The construction introduces a linear number of fresh variables, so the
reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _new_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a one‑element list so that the integer can be mutated in‑
    place without using ``global``.
    """
    counter[0] += 1
    return counter[0]

# An unsatisfiable 3‑SAT core using three variables. It contains all eight
# possible clauses over variables 1,2,3. For any assignment, the clause that
# consists of the negated literals of that assignment is falsified, so the
# formula is unsatisfiable.
_UNSAT_CORE = {
    "num_vars": 3,
    "clauses": [
        [1, 2, 3],
        [1, 2, -3],
        [1, -2, 3],
        [1, -2, -3],
        [-1, 2, 3],
        [-1, 2, -3],
        [-1, -2, 3],
        [-1, -2, -3],
    ],
}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The function assumes ``instance`` has already been validated by
    ``Sat.validate``.  It returns a dictionary that satisfies
    ``ThreeSat.validate``.
    """
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Preprocess clauses: remove duplicate literals, drop tautologies, and
    # handle empty clauses.
    processed: List[List[int]] = []
    for cl in clauses:
        if len(cl) == 0:
            # Empty clause -> unsatisfiable.
            return {"num_vars": _UNSAT_CORE["num_vars"], "clauses": list(_UNSAT_CORE["clauses"])}
        lit_map: Dict[int, int] = {}
        tautology = False
        for lit in cl:
            var = abs(lit)
            if var in lit_map:
                if lit_map[var] != lit:
                    # both v and -v present -> clause always true.
                    tautology = True
                    break
                # same literal repeated – ignore.
            else:
                lit_map[var] = lit
        if tautology:
            # Clause satisfied for any assignment; skip it.
            continue
        simplified = list(lit_map.values())
        if not simplified:
            return {"num_vars": _UNSAT_CORE["num_vars"], "clauses": list(_UNSAT_CORE["clauses"])}
        processed.append(simplified)

    fresh_counter = [m]
    new_clauses: List[List[int]] = []

    for cl in processed:
        k = len(cl)
        if k == 1:
            a = _new_var(fresh_counter)
            b = _new_var(fresh_counter)
            l = cl[0]
            new_clauses.append([l, a, b])
            new_clauses.append([l, a, -b])
            new_clauses.append([l, -a, b])
            new_clauses.append([l, -a, -b])
        elif k == 2:
            a = _new_var(fresh_counter)
            l1, l2 = cl
            new_clauses.append([l1, l2, a])
            new_clauses.append([l1, l2, -a])
        elif k == 3:
            new_clauses.append(cl.copy())
        else:
            literals = cl
            y_prev = _new_var(fresh_counter)
            new_clauses.append([literals[0], literals[1], y_prev])
            for i in range(2, k - 2):
                y_curr = _new_var(fresh_counter)
                new_clauses.append([-y_prev, literals[i], y_curr])
                y_prev = y_curr
            new_clauses.append([-y_prev, literals[-2], literals[-1]])

    result = {"num_vars": fresh_counter[0], "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

