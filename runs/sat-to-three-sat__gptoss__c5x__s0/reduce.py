"""Reduction from SAT to 3‑SAT.

The source problem is :class:`Sat` defined in *problems.py* and the target
problem is :class:`ThreeSat`.  Both classes only provide a ``validate``
method; they do not contain solvers.  This module implements a polynomial‑time
reduction that respects the exact instance formats described in the doc‑strings
of those classes.

The reduction is the classic textbook transformation:

* Empty clause → produce a fixed unsatisfiable 3‑SAT instance (all eight
  possible clauses over three fresh variables).  The whole formula is then
  unsatisfiable, matching the source semantics.
* Clause of length 1: ``(l)`` is replaced by four clauses that together are
  satisfiable iff ``l`` is true.  Fresh variables ``y`` and ``z`` are used:
  ``(l ∨  y ∨  z)``, ``(l ∨  y ∨ ¬z)``, ``(l ∨ ¬y ∨  z)``, ``(l ∨ ¬y ∨ ¬z)``.
  If ``l`` is false the four clauses are contradictory, otherwise they are
  trivially satisfied.
* Clause of length 2: ``(l1 ∨ l2)`` is replaced by two clauses using a fresh
  variable ``y``: ``(l1 ∨ l2 ∨  y)`` and ``(l1 ∨ l2 ∨ ¬y)``.  The pair is
  satisfiable exactly when ``l1 ∨ l2`` holds.
* Clause of length ≥3: we use the standard chain‑variable construction.  For a
  clause ``(l1 ∨ … ∨ lk)`` with ``k > 3`` we introduce fresh variables
  ``y1,…,y_{k‑3}`` and create the following 3‑literal clauses:

  ``(l1 ∨ l2 ∨ y1)``
  ``(¬y1 ∨ l3 ∨ y2)``
  `` … ``
  ``(¬y_{k‑4} ∨ l_{k‑2} ∨ y_{k‑3})``
  ``(¬y_{k‑3} ∨ l_{k‑1} ∨ l_k)``

  This construction preserves satisfiability and uses only distinct variables
  inside each clause, satisfying the validation rules of :class:`ThreeSat`.

The implementation below follows this description, tracks the next fresh
variable index, and finally returns a dictionary that validates against
``ThreeSat.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _unsat_three_sat(start_var: int) -> Dict[str, Any]:
    """Return a small unsatisfiable 3‑SAT instance.

    We use three fresh variables ``a, b, c`` (starting at ``start_var``) and
    generate all eight possible clauses over them.  The conjunction of all
    eight clauses is unsatisfiable because every assignment falsifies at least
    one clause.
    """
    a, b, c = start_var, start_var + 1, start_var + 2
    clauses: List[List[int]] = []
    for mask in range(8):
        lit_a = a if (mask & 1) else -a
        lit_b = b if (mask & 2) else -b
        lit_c = c if (mask & 4) else -c
        clauses.append([lit_a, lit_b, lit_c])
    return {"num_vars": c, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The function runs in time polynomial in the size of *instance* and returns
    a dictionary that validates against :class:`ThreeSat`.
    """
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # If any clause is empty the formula is unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        start = max(1, num_vars + 1)
        return _unsat_three_sat(start)

    # ------------------------------------------------------------------
    # Pre‑process SAT clauses: remove tautologies and duplicate literals.
    # ------------------------------------------------------------------
    processed: List[List[int]] = []
    for clause in clauses:
        lits_set = set()
        tautology = False
        for lit in clause:
            if -lit in lits_set:
                tautology = True
                break
            lits_set.add(lit)
        if tautology:
            continue  # clause always true, can be omitted
        processed.append(list(lits_set))

    new_clauses: List[List[int]] = []
    next_var = num_vars + 1

    for clause in processed:
        k = len(clause)
        if k == 0:
            # Should not happen after earlier check, but keep safety.
            start = max(1, num_vars + 1)
            return _unsat_three_sat(start)
        if k == 1:
            l = clause[0]
            y, z = next_var, next_var + 1
            next_var += 2
            new_clauses.extend([
                [l, y, z],
                [l, y, -z],
                [l, -y, z],
                [l, -y, -z],
            ])
        elif k == 2:
            l1, l2 = clause
            y = next_var
            next_var += 1
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        elif k == 3:
            new_clauses.append(clause.copy())
        else:
            # k > 3 – chain construction.
            lits = clause
            y_prev = next_var
            next_var += 1
            new_clauses.append([lits[0], lits[1], y_prev])
            for i in range(2, k - 1):
                if i == k - 2:
                    new_clauses.append([-y_prev, lits[i], lits[i + 1]])
                else:
                    y_new = next_var
                    next_var += 1
                    new_clauses.append([-y_prev, lits[i], y_new])
                    y_prev = y_new

    result = {"num_vars": next_var - 1, "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

