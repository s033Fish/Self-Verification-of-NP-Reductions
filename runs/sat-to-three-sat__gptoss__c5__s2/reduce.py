"""Reduction from SAT to 3‑SAT.

The source problem is :class:`Sat` defined in ``problems.py``.  An instance
has the form ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where each
clause may contain any number of literals (including zero).

The target problem is :class:`ThreeSat`.  Its instances must have exactly three
distinct literals per clause and no clause may contain both a variable and its
negation.

The implementation follows the classic polynomial‑time reduction:

* Empty clause → produce an unsatisfiable 3‑SAT formula.
* Clause of size 1 → pad with two fresh variables that are forced to be false.
* Clause of size 2 → pad with one fresh variable forced to be false.
* Clause of size ≥3 → replace with a chain of 3‑literal clauses using fresh
  auxiliary variables (the standard Tseitin‑style construction).

Forcing a variable ``v`` to be **false** (or **true**) is done by introducing
two fresh helper variables ``a`` and ``b`` and adding the four clauses that
exclude every possible assignment to ``a`` and ``b`` when ``v`` has the
undesired truth value.  Concretely, to force ``v`` false we add the clauses

``[-v,  a,  b]``
``[-v,  a, -b]``
``[-v, -a,  b]``
``[-v, -a, -b]``

If ``v`` were true, the four clauses would forbid all 2‑bit assignments to
``a`` and ``b`` – an impossibility – therefore ``v`` must be false.  The same
pattern with ``v`` (positive) forces ``v`` to be true.

All newly introduced variables receive fresh identifiers greater than the
original ``num_vars``.  The returned instance conforms to the ``ThreeSat``
validation rules.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _force_false(var: int, next_var: int, clauses: List[List[int]]) -> int:
    a = next_var
    b = next_var + 1
    clauses.append([-var, a, b])
    clauses.append([-var, a, -b])
    clauses.append([-var, -a, b])
    clauses.append([-var, -a, -b])
    return next_var + 2


def _force_true(var: int, next_var: int, clauses: List[List[int]]) -> int:
    a = next_var
    b = next_var + 1
    clauses.append([var, a, b])
    clauses.append([var, a, -b])
    clauses.append([var, -a, b])
    clauses.append([var, -a, -b])
    return next_var + 2


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    Sat.validate(instance)
    m = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]
    new_clauses: List[List[int]] = []
    next_var = m + 1

    def fresh() -> int:
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    unsat = False

    for clause in original_clauses:
        # Remove duplicate literals and detect tautological clauses.
        var_sign: dict[int, int] = {}
        tautology = False
        for lit in clause:
            v = abs(lit)
            s = 1 if lit > 0 else -1
            if v in var_sign:
                if var_sign[v] != s:
                    tautology = True
                    break
            else:
                var_sign[v] = s
        if tautology:
            continue  # clause always satisfied, can be ignored
        simplified = [s * v for v, s in var_sign.items()]
        k = len(simplified)
        if k == 0:
            # original clause was empty
            unsat = True
            break
        if k == 1:
            a = fresh()
            b = fresh()
            new_clauses.append([simplified[0], a, b])
            next_var = _force_false(a, next_var, new_clauses)
            next_var = _force_false(b, next_var, new_clauses)
        elif k == 2:
            a = fresh()
            new_clauses.append([simplified[0], simplified[1], a])
            next_var = _force_false(a, next_var, new_clauses)
        else:
            # k >= 3
            if k == 3:
                new_clauses.append(simplified)
            else:
                # introduce auxiliary variables y1..y_{k-3}
                aux_vars = []
                for _ in range(k - 3):
                    aux_vars.append(fresh())
                # first clause
                new_clauses.append([simplified[0], simplified[1], aux_vars[0]])
                # middle clauses
                for i in range(1, k - 3):
                    new_clauses.append([-aux_vars[i - 1], simplified[i + 1], aux_vars[i]])
                # last clause
                new_clauses.append([-aux_vars[-1], simplified[-2], simplified[-1]])

    if unsat:
        p = fresh()
        next_var = _force_true(p, next_var, new_clauses)
        next_var = _force_false(p, next_var, new_clauses)

    result = {"num_vars": next_var - 1, "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

