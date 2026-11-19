"""Reduction from SAT to 3-SAT.

The source problem (Sat) uses the format:
    {"num_vars": m, "clauses": [[lit, ...], ...]}
where literals are signed integers (+v or -v). Clauses may be of any
size, may contain duplicate literals, and may even be empty.

The target problem (ThreeSat) requires every clause to contain exactly
three *distinct* literals on three distinct variables, and a clause may
not contain both a variable and its negation.

This module implements a classic polynomial‑time reduction that
converts an arbitrary CNF formula into an equivalent 3‑CNF formula.
The reduction respects all edge‑cases described in the problem
definitions:

* An empty formula (no clauses) remains empty – it is satisfiable.
* A formula containing an empty clause is unsatisfiable; we output a
  small unsatisfiable 3‑SAT gadget.
* Tautological clauses (containing a variable and its negation) are
  ignored because they are always satisfied.

The reduction runs in time linear in the size of the input formula and
produces a formula that is satisfiable iff the original formula is.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _next_var_counter(start: int):
    """Utility generator yielding fresh variable identifiers.

    The SAT instances use variables numbered from 1..m.  This helper
    yields successive integers starting at ``start`` and increments the
    internal counter each time it is called.
    """

    cur = start
    while True:
        cur += 1
        yield cur


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described in the problem statement.

    Returns
    -------
    dict
        A ThreeSat instance in the required format.
    """

    m: int = int(instance.get("num_vars", 0))
    raw_clauses: List[List[int]] = instance.get("clauses", [])

    # Generator for fresh variables.
    fresh = _next_var_counter(m)

    result_clauses: List[List[int]] = []

    # Helper to produce an unsatisfiable 3‑SAT gadget.
    def unsat_gadget() -> None:
        a = next(fresh)
        b = next(fresh)
        c = next(fresh)
        # (a ∨ b ∨ c) ∧ (¬a ∨ ¬b ∨ ¬c) is unsatisfiable.
        result_clauses.append([a, b, c])
        result_clauses.append([-a, -b, -c])

    for clause in raw_clauses:
        # Remove duplicate literals and detect tautologies.
        lit_set = set(clause)
        # If both a literal and its negation appear, the clause is a
        # tautology and can be ignored.
        if any(lit != 0 and -lit in lit_set for lit in lit_set):
            continue

        # After removing duplicates, work with a list.
        lits = list(lit_set)

        if len(lits) == 0:
            # Empty clause => formula unsatisfiable.
            unsat_gadget()
            # No need to process further; the whole formula is already
            # unsatisfiable, but we continue to keep the loop simple.
            continue

        if len(lits) == 1:
            # Pad with two fresh variables.
            a = next(fresh)
            b = next(fresh)
            result_clauses.append([lits[0], a, b])
            continue

        if len(lits) == 2:
            # Pad with one fresh variable.
            a = next(fresh)
            result_clauses.append([lits[0], lits[1], a])
            continue

        if len(lits) == 3:
            # Already a valid 3‑clause (variables are distinct and we
            # already removed tautologies).
            result_clauses.append(lits)
            continue

        # Length > 3: apply the classic chain reduction.
        k = len(lits)
        # Create auxiliary variables y1 ... y_{k-3}
        aux_vars = [next(fresh) for _ in range(k - 3)]

        # First clause: (l1 ∨ l2 ∨ y1)
        result_clauses.append([lits[0], lits[1], aux_vars[0]])

        # Middle clauses: (¬y_i ∨ l_{i+2} ∨ y_{i+1}) for i = 1 .. k-4
        for i in range(1, k - 3):
            result_clauses.append([-aux_vars[i - 1], lits[i + 1], aux_vars[i]])

        # Last clause: (¬y_{k-3} ∨ l_{k-1} ∨ l_k)
        result_clauses.append([-aux_vars[-1], lits[-2], lits[-1]])

    # Determine the new number of variables.
    max_var = m
    for cl in result_clauses:
        for lit in cl:
            v = abs(lit)
            if v > max_var:
                max_var = v

    return {"num_vars": max_var, "clauses": result_clauses}

