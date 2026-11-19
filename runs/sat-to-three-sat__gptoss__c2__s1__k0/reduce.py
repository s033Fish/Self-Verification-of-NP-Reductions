"""Reduction from SAT to 3-SAT.

The source problem (SAT) allows clauses of arbitrary length (including the
empty clause) and may contain duplicate literals or a literal together with its
negation.  The target problem (ThreeSat) requires every clause to contain **exactly**
three *different* variables, none of which appear both positively and
negatively in the same clause.

This module implements a polynomial‑time many‑one reduction.  The algorithm is
the classic textbook construction:

* A clause of length ``k ≥ 3`` is broken into a chain of 3‑clauses using fresh
  auxiliary variables.
* A clause of length 2 is padded with a fresh variable ``y`` producing the two
  clauses ``(l1 ∨ l2 ∨  y)`` and ``(l1 ∨ l2 ∨ ¬y)``.
* A clause of length 1 is enforced by four clauses that together are
  equivalent to the unit clause.
* An empty clause makes the whole formula unsatisfiable.  In this case we
  output a fixed unsatisfiable 3‑CNF over three fresh variables.  The set of the
  eight possible 3‑clauses on three variables is unsatisfiable because each
  assignment falsifies exactly one of them.

The implementation follows the specification of the ``Sat`` and ``ThreeSat``
problems described in ``problems.py``.  Literals are represented as signed
integers: ``+v`` for the positive literal and ``-v`` for the negated literal.
"""

from __future__ import annotations

from typing import List, Dict

def _unsat_core() -> Dict:
    """Return a fixed unsatisfiable 3‑SAT instance over three variables.

    For every assignment to variables 1, 2, 3 we create the clause that is
    falsified by that assignment.  The resulting eight clauses cannot be
    simultaneously satisfied.
    """
    clauses: List[List[int]] = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                # literal is positive if the variable is assigned False (0)
                # and negative if the variable is assigned True (1).
                clause = []
                clause.append(-1 if a else 1)
                clause.append(-2 if b else 2)
                clause.append(-3 if c else 3)
                clauses.append(clause)
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies the ``ThreeSat`` format described in
    ``problems.py``.  The transformation runs in time polynomial in the size of
    the input.
    """
    m: int = instance.get("num_vars", 0)
    orig_clauses: List[List[int]] = instance.get("clauses", [])

    # If any clause is empty, the formula is unsatisfiable.  Return a fixed
    # unsatisfiable core (the exact variables used do not matter).
    for cl in orig_clauses:
        if len(cl) == 0:
            return _unsat_core()

    new_clauses: List[List[int]] = []
    next_var = m + 1  # first fresh variable index

    for cl in orig_clauses:
        # Remove duplicate literals and detect trivially satisfied clauses.
        lits_set = set(cl)
        # If a clause contains both v and -v it is always satisfied; we can skip it.
        skip = False
        for lit in lits_set:
            if -lit in lits_set:
                skip = True
                break
        if skip:
            continue

        # Remove duplicates (set already does that) and sort for determinism.
        lits = list(lits_set)

        k = len(lits)
        if k == 0:
            # Should have been caught earlier, but keep safety.
            return _unsat_core()
        elif k == 1:
            # Unit clause: enforce with four 3‑clauses using two fresh vars.
            y = next_var
            next_var += 1
            z = next_var
            next_var += 1
            l = lits[0]
            new_clauses.extend([
                [l,  y,  z],
                [l,  y, -z],
                [l, -y,  z],
                [l, -y, -z],
            ])
        elif k == 2:
            # Binary clause: pad with a fresh variable y.
            y = next_var
            next_var += 1
            l1, l2 = lits
            new_clauses.append([l1, l2,  y])
            new_clauses.append([l1, l2, -y])
        elif k == 3:
            # Already a proper 3‑clause.
            new_clauses.append(lits)
        else:
            # k > 3: break into a chain of 3‑clauses.
            # We will introduce (k-3) fresh variables y1..y_{k-3}.
            # Clause 1: (l1 ∨ l2 ∨ y1)
            # Clause i (2 ≤ i ≤ k-3): (¬y_{i-1} ∨ l_{i+1} ∨ y_i)
            # Final clause: (¬y_{k-3} ∨ l_{k-1} ∨ l_k)
            # Ensure all fresh vars are distinct from original ones.
            # First clause
            y_prev = next_var
            next_var += 1
            new_clauses.append([lits[0], lits[1],  y_prev])
            # Intermediate clauses
            for i in range(2, k - 1):  # i indexes the literal being added
                if i == k - 1:
                    # Last clause handled after the loop
                    break
                y_curr = next_var
                next_var += 1
                new_clauses.append([-y_prev, lits[i], y_curr])
                y_prev = y_curr
            # Final clause using the last two literals
            new_clauses.append([-y_prev, lits[-2], lits[-1]])

    # The total number of variables is the original plus any fresh ones created.
    total_vars = next_var - 1
    return {"num_vars": total_vars, "clauses": new_clauses}

