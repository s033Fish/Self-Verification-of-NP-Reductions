"""Reduction from SAT to 3‑SAT.

The source problem is :class:`Sat` defined in ``problems.py``. An instance is a
dictionary ``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where a
literal is a signed integer ``+v`` (meaning variable *v* is true) or ``-v``
(meaning variable *v* is false). Clauses may have any length, including 0.

The target problem is :class:`ThreeSat`. Its instances must have **exactly**
three literals per clause, each on a *different* variable and without both a
variable and its negation appearing in the same clause.

The reduction follows the classic textbook construction:

* Empty clause → produce a globally unsatisfiable 3‑SAT formula (all 8 possible
  3‑literal clauses over three fresh variables). Any formula containing an
  empty clause is unsatisfiable, so the whole reduction can return this fixed
  unsatisfiable instance.
* Unit clause ``(l)`` → introduce two fresh variables ``y`` and ``z`` and add
  the four clauses

    ``[l,  y,  z]``, ``[l,  y, -z]``, ``[l, -y,  z]``, ``[l, -y, -z]``.

  If ``l`` is true all clauses are satisfied; if ``l`` is false the four
  clauses become a classic unsatisfiable set because they require ``y`` and
  ``z`` to simultaneously be true and false.
* Binary clause ``(l1 ∨ l2)`` → introduce one fresh variable ``y`` and add the
  two clauses ``[l1, l2,  y]`` and ``[l1, l2, -y]``. When ``l1`` or ``l2`` is
  true both clauses are satisfied; when both are false the pair forces ``y`` to
  be both true and false, making the formula unsatisfiable.
* Longer clause ``(l1 ∨ … ∨ lk)`` with ``k ≥ 3`` → introduce fresh
  auxiliary variables ``y1 … y_{k‑3}`` and create the chain

    ``[l1, l2,  y1]``, ``[-y1, l3,  y2]``, …,
    ``[-y_{k‑4}, l_{k‑2},  y_{k‑3}]``, ``[-y_{k‑3}, l_{k‑1}, l_k]``.

  This is the standard reduction that preserves satisfiability.

All fresh variables are distinct and never clash with the original variables.
The construction runs in time linear in the total size of the input formula,
hence polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _unsat_three_sat() -> Dict[str, Any]:
    """Return a fixed unsatisfiable 3‑SAT instance.

    We use three variables (1, 2, 3) and include **all** eight possible
    clauses of size three with distinct variables. For any assignment at
    least one of these clauses is falsified, so the whole formula is
    unsatisfiable.
    """
    vars_ = [1, 2, 3]
    clauses: List[List[int]] = []
    for mask in range(8):
        clause = []
        for i, v in enumerate(vars_):
            sign = 1 if (mask >> i) & 1 else -1
            clause.append(sign * v)
        clauses.append(clause)
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies ``ThreeSat.validate`` and is satisfiable
    iff the input ``instance`` is satisfiable.
    """
    Sat.validate(instance)
    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # If any clause is empty, the formula is unsatisfiable.
    for c in clauses:
        if len(c) == 0:
            return _unsat_three_sat()

    new_clauses: List[List[int]] = []
    next_var = num_vars

    def fresh() -> int:
        nonlocal next_var
        next_var += 1
        return next_var

    for clause in clauses:
        # Simplify clause: remove duplicate literals on same variable and
        # detect tautologies (both a variable and its negation).
        var_sign: dict[int, int] = {}
        tautology = False
        for lit in clause:
            v = abs(lit)
            if v in var_sign:
                if var_sign[v] != lit:
                    tautology = True
                    break
            else:
                var_sign[v] = lit
        if tautology:
            # Clause always true, can be omitted.
            continue
        lits = list(var_sign.values())
        k = len(lits)
        if k == 0:
            # After removing duplicates the clause became empty, which means it
            # was a tautology; already handled.
            continue
        if k == 1:
            l = lits[0]
            y = fresh()
            z = fresh()
            new_clauses.append([l,  y,  z])
            new_clauses.append([l,  y, -z])
            new_clauses.append([l, -y,  z])
            new_clauses.append([l, -y, -z])
        elif k == 2:
            l1, l2 = lits
            y = fresh()
            new_clauses.append([l1, l2,  y])
            new_clauses.append([l1, l2, -y])
        else:
            # k >= 3
            if k == 3:
                new_clauses.append([lits[0], lits[1], lits[2]])
            else:
                y_prev = fresh()
                new_clauses.append([lits[0], lits[1],  y_prev])
                for i in range(2, k - 1):
                    y_next = fresh()
                    new_clauses.append([-y_prev, lits[i],  y_next])
                    y_prev = y_next
                new_clauses.append([-y_prev, lits[-2], lits[-1]])

    result = {"num_vars": next_var, "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

