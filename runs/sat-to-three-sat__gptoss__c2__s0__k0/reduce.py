"""Reduction from SAT to 3-SAT.

The source problem ``Sat`` expects instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where each ``literal`` is an integer ``+v`` (variable ``v`` is true) or
``-v`` (variable ``v`` is false).  Clauses may contain any number of
literals (including zero) and may repeat literals.

The target problem ``ThreeSat`` requires every clause to contain exactly
three *distinct* variables and no clause may contain both a variable and
its negation.

This module implements the classic polynomial‑time reduction that
converts an arbitrary CNF formula into an equivalent 3‑CNF formula.
The reduction handles all edge cases described in the problem
definitions:

* An empty list of clauses is mapped to an empty list of 3‑clauses –
  both are trivially satisfiable.
* If any clause in the input is empty (i.e. ``[]``) the instance is
  unsatisfiable.  We return a fixed unsatisfiable 3‑SAT gadget consisting
  of the eight possible clauses over three fresh variables.  For any
  assignment exactly one of those eight clauses evaluates to false, so
  the whole formula is unsatisfiable.

The reduction follows the textbook construction:

* Unit clause ``(l)`` → four 3‑clauses forcing ``l`` to be true.
* Binary clause ``(l1 ∨ l2)`` → two 3‑clauses using a fresh variable ``y``.
* Longer clause ``(l1 ∨ … ∨ lk)`` (k ≥ 3) → a chain of ``k‑2``
  3‑clauses introducing ``k‑3`` fresh variables.

All newly introduced variables are given indices larger than the
original ``num_vars`` to avoid clashes.
"""

from typing import List, Dict


def _unsat_gadget(start_var: int) -> List[List[int]]:
    """Return eight 3‑clauses over three fresh variables that are jointly
    unsatisfiable.

    The variables are ``start_var``, ``start_var+1`` and ``start_var+2``.
    For each combination of signs we create a clause ``[s1*v1, s2*v2,
    s3*v3]`` where ``s`` is either ``+`` or ``-``.  Among the eight
    possible assignments exactly one clause (the one whose literals are
    the negations of the assignment) is falsified, making the whole
    formula unsatisfiable.
    """
    v1, v2, v3 = start_var, start_var + 1, start_var + 2
    signs = [1, -1]
    clauses: List[List[int]] = []
    for s1 in signs:
        for s2 in signs:
            for s3 in signs:
                clauses.append([s1 * v1, s2 * v2, s3 * v3])
    return clauses


def reduce(instance: Dict) -> Dict:
    """Convert a SAT instance to an equivalent 3‑SAT instance.

    The function runs in time polynomial in the size of the input.
    It does **not** invoke any solver.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: formula with no clauses – trivially satisfiable.
    if not clauses:
        return {"num_vars": m, "clauses": []}

    # Detect an empty clause which makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            start = max(m, 0) + 1
            unsat = _unsat_gadget(start)
            return {"num_vars": start + 2, "clauses": unsat}

    # -----------------------------------------------------------------
    # Clean clauses: remove duplicate literals and discard tautological
    # clauses (containing a variable both positively and negatively).
    # After this step each clause contains distinct variables and never a
    # literal and its negation.
    # -----------------------------------------------------------------
    cleaned: List[List[int]] = []
    for cl in clauses:
        lit_set = set()
        tautology = False
        for lit in cl:
            if -lit in lit_set:
                tautology = True
                break
            lit_set.add(lit)
        if tautology:
            # Clause always true – can be omitted.
            continue
        cleaned.append(list(lit_set))

    new_clauses: List[List[int]] = []
    next_var = m + 1  # first fresh variable index

    for cl in cleaned:
        k = len(cl)
        if k == 1:
            # Unit clause – force the literal to be true.
            l = cl[0]
            y1 = next_var
            y2 = next_var + 1
            next_var += 2
            new_clauses.extend([
                [l, y1, y2],
                [l, y1, -y2],
                [l, -y1, y2],
                [l, -y1, -y2],
            ])
        elif k == 2:
            # Binary clause – use one fresh variable.
            l1, l2 = cl
            y = next_var
            next_var += 1
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        else:
            # k >= 3 – break into a chain of 3‑clauses.
            lits = cl[:]  # copy
            # First clause uses first two literals and a fresh y.
            y_prev = next_var
            next_var += 1
            new_clauses.append([lits[0], lits[1], y_prev])
            # Intermediate clauses.
            for i in range(2, k - 1):
                y_new = next_var
                next_var += 1
                new_clauses.append([-y_prev, lits[i], y_new])
                y_prev = y_new
            # Final clause uses the last literal, the previous y, and the
            # second‑last literal to keep exactly three literals.
            new_clauses.append([-y_prev, lits[-1], lits[-2]])

    return {"num_vars": next_var - 1, "clauses": new_clauses}

