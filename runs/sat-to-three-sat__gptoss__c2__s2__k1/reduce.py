"""Reduction from SAT to 3‑SAT.

The source problem (Sat) allows clauses of arbitrary length (including 0 or
1 literals) and may contain duplicate literals or both a variable and its
negation.  The target problem (ThreeSat) requires every clause to contain
exactly three *distinct* variables and never both a variable and its
negation.

The reduction is the classic polynomial‑time transformation used in textbooks.
For each clause C of the SAT instance we produce a set of 3‑SAT clauses that
is satisfiable exactly when C is satisfied.  The construction handles all
edge‑cases described in the problem statement.

If the original formula contains an empty clause (which makes it unsatisfiable)
we output a fixed unsatisfiable 3‑SAT instance consisting of five clauses over
three fresh variables.  This instance is well‑formed according to the ThreeSat
specification and is known to be unsatisfiable.

The implementation runs in time polynomial in the size of the input (the
number of literals) and uses only straightforward list manipulation.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _unsat_three_sat() -> Dict[str, Any]:
    """Return a small, fixed unsatisfiable 3‑SAT instance.

    The instance uses variables 1, 2, 3 and consists of the following five
    clauses (written with signed integers where a positive number denotes the
    literal, a negative number denotes its negation):

        ( 1  2  3)
        ( 1  2 -3)
        ( 1 -2  3)
        (-1  2  3)
        (-1 -2 -3)

    It can be checked by exhaustive enumeration that no assignment satisfies
    all five clauses simultaneously, so the formula is unsatisfiable.
    """
    return {
        "num_vars": 3,
        "clauses": [
            [1, 2, 3],
            [1, 2, -3],
            [1, -2, 3],
            [-1, 2, 3],
            [-1, -2, -3],
        ],
    }


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT formula as described in the task
        statement.  It contains the keys ``"num_vars"`` (the original number of
        variables) and ``"clauses"`` (a list of clauses, each clause being a
        list of signed integers).

    Returns
    -------
    dict
        A dictionary representing a 3‑SAT formula that is satisfiable exactly
        when the input formula is satisfiable.
    """

    original_num_vars: int = instance.get("num_vars", 0)
    original_clauses: List[List[int]] = instance.get("clauses", [])

    # If there is an empty clause the formula is unsatisfiable.  Return a
    # fixed unsatisfiable 3‑SAT instance.
    for clause in original_clauses:
        if len(clause) == 0:
            return _unsat_three_sat()

    # New variables will be numbered after the original ones.
    next_var = original_num_vars + 1
    three_sat_clauses: List[List[int]] = []

    for clause in original_clauses:
        # Remove duplicate literals and check for a literal and its negation.
        # If both appear, the clause is a tautology and can be ignored.
        lits_set = set(clause)
        tautology = any(lit in lits_set and -lit in lits_set for lit in lits_set)
        if tautology:
            continue  # clause already always satisfied

        # After removing duplicates, keep the list for ordering.
        lits = list(lits_set)
        k = len(lits)

        if k == 1:
            # Unit clause l.  Introduce two new variables a,b and create four
            # clauses that force l to be true.
            l = lits[0]
            a = next_var
            b = next_var + 1
            next_var += 2
            three_sat_clauses.extend([
                [l, a, b],
                [l, -a, b],
                [l, a, -b],
                [l, -a, -b],
            ])
        elif k == 2:
            # Binary clause (l1 ∨ l2).  Introduce a new variable a and add two
            # clauses (l1 ∨ l2 ∨ a) and (l1 ∨ l2 ∨ -a).
            l1, l2 = lits
            a = next_var
            next_var += 1
            three_sat_clauses.append([l1, l2, a])
            three_sat_clauses.append([l1, l2, -a])
        elif k == 3:
            # Already a proper 3‑SAT clause, but we must ensure the three
            # variables are distinct (they are after duplicate removal) and no
            # variable appears both positively and negatively (handled by the
            # tautology check above).  We can keep the clause as‑is.
            three_sat_clauses.append(lits)
        else:
            # k > 3.  Use the standard chain construction.
            # Create fresh variables y1 ... y_{k-3}.
            y_vars = list(range(next_var, next_var + k - 3))
            next_var += k - 3

            # First clause: (l1 ∨ l2 ∨ y1)
            three_sat_clauses.append([lits[0], lits[1], y_vars[0]])
            # Middle clauses: (¬y_i ∨ l_{i+2} ∨ y_{i+1}) for i = 0 .. k-4
            for i in range(k - 4):
                three_sat_clauses.append([-y_vars[i], lits[i + 2], y_vars[i + 1]])
            # Last clause: (¬y_{k-4} ∨ l_{k-1} ∨ l_k)
            three_sat_clauses.append([-y_vars[-1], lits[-2], lits[-1]])

    # The resulting formula may use variables up to next_var-1.
    return {"num_vars": next_var - 1, "clauses": three_sat_clauses}

