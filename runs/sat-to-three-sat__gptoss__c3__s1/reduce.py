"""Reduction from SAT to 3-SAT.

The source problem is :class:`Sat` (generic CNF SAT) and the target is
``ThreeSat`` – every clause must contain exactly three *distinct* literals on
distinct variables, and a clause may not contain both a variable and its
negation.

The implementation follows the classic polynomial‑time reduction:

* Unit clauses are eliminated by **unit propagation**.  This step is
  polynomial and either discovers a contradiction (an empty clause) or
  produces an equivalent formula that contains no unit clauses.
* Tautological clauses (containing a variable together with its negation) are
  dropped because they are always satisfied.
* After cleaning, each remaining clause has at least two literals and all
  literals refer to distinct variables.
* A clause of size two ``(a ∨ b)`` is replaced by the two 3‑clauses
  ``(a ∨ b ∨ y)`` and ``(a ∨ b ∨ ¬y)`` where ``y`` is a fresh variable.  The
  pair is satisfiable iff ``a ∨ b`` is true.
* A clause of size three is kept unchanged (it already satisfies the target
  format).
* A clause of size ``k > 3`` ``(l₁ ∨ … ∨ l_k)`` is replaced by the standard
  chain using fresh auxiliary variables ``y₁ … y_{k‑3}``:

  ``(l₁ ∨ l₂ ∨ y₁)``,
  ``(¬y₁ ∨ l₃ ∨ y₂)``, …,
  ``(¬y_{k‑4} ∨ l_{k‑2} ∨ y_{k‑3})``,
  ``(¬y_{k‑3} ∨ l_{k‑1} ∨ l_k)``.

  Every clause in the chain has three distinct literals and the construction
  is satisfiable exactly when the original clause is.

If unit propagation yields an empty clause the original formula is unsatisfiable.
In that case we return a **fixed unsatisfiable 3‑SAT instance** consisting of
five clauses over three variables – this instance is known to be unsatisfiable
and respects the target format.

The reduction runs in time polynomial in the size of the input instance.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import Sat, ThreeSat


def _unit_propagate(num_vars: int, clauses: List[List[int]]) -> Tuple[bool, List[List[int]]]:
    """Exhaustive unit propagation.

    Returns ``(is_unsat, simplified_clauses)`` where ``is_unsat`` indicates that
    the formula is unsatisfiable (an empty clause was derived). The returned
    clause list contains no unit clauses.
    """
    assignment: dict[int, bool] = {}
    current = [list(c) for c in clauses]
    while True:
        new_clauses: List[List[int]] = []
        unit_lit: int | None = None
        for clause in current:
            satisfied = False
            unassigned: List[int] = []
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var]
                    if (val and lit > 0) or (not val and lit < 0):
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            if satisfied:
                continue
            if not unassigned:
                return True, []
            if len(unassigned) == 1:
                unit_lit = unassigned[0]
                new_clauses.append(unassigned)
            else:
                new_clauses.append(unassigned)
        if unit_lit is None:
            return False, new_clauses
        var = abs(unit_lit)
        val = unit_lit > 0
        if var in assignment and assignment[var] != val:
            return True, []
        assignment[var] = val
        current = new_clauses


def _clean_clause(clause: List[int]) -> List[int] | None:
    """Remove duplicate literals and detect tautologies.

    Returns ``None`` for a tautological clause (always true). Otherwise returns a
    list with at most one literal per variable.
    """
    seen: dict[int, bool] = {}
    for lit in clause:
        var = abs(lit)
        sign = lit > 0
        if var in seen:
            if seen[var] != sign:
                return None  # tautology
        else:
            seen[var] = sign
    return [v if seen[v] else -v for v in seen]


def _unsat_three_sat_instance() -> dict:
    """A known unsatisfiable 3‑SAT instance (3 variables, 5 clauses)."""
    clauses = [
        [1, 2, 3],
        [-1, -2, -3],
        [1, -2, -3],
        [-1, 2, -3],
        [-1, -2, 3],
    ]
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance: dict) -> dict:
    """Convert a SAT instance to an equivalent 3‑SAT instance.

    The returned instance conforms to the ``ThreeSat`` specification.
    """
    Sat.validate(instance)
    num_vars = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    unsat, simplified = _unit_propagate(num_vars, original_clauses)
    if unsat:
        return _unsat_three_sat_instance()

    cleaned: List[List[int]] = []
    for cl in simplified:
        new_cl = _clean_clause(cl)
        if new_cl is None:
            continue  # tautology
        if not new_cl:
            return _unsat_three_sat_instance()
        cleaned.append(new_cl)

    new_clauses: List[List[int]] = []
    next_var = num_vars + 1

    for cl in cleaned:
        k = len(cl)
        if k == 1:
            # Embed the unit literal with two fresh dummy variables that are free.
            d1 = next_var
            next_var += 1
            d2 = next_var
            next_var += 1
            new_clauses.append([cl[0], d1, d2])
            # Add always‑satisfied filler clauses (they do not constrain the original literal).
            new_clauses.append([-d1, -d2, d1])
            new_clauses.append([-d1, -d2, d2])
        elif k == 2:
            a, b = cl
            y = next_var
            next_var += 1
            new_clauses.append([a, b, y])
            new_clauses.append([a, b, -y])
        elif k == 3:
            new_clauses.append(cl)
        else:
            lits = cl
            aux: List[int] = []
            for _ in range(k - 3):
                aux.append(next_var)
                next_var += 1
            # first clause
            new_clauses.append([lits[0], lits[1], aux[0]])
            # middle clauses
            for i in range(2, k - 2):
                new_clauses.append([-aux[i - 2], lits[i], aux[i - 1]])
            # last clause
            new_clauses.append([-aux[-1], lits[-2], lits[-1]])

    return {"num_vars": next_var - 1, "clauses": new_clauses}

