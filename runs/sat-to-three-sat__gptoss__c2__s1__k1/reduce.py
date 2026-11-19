"""Reduction from SAT to 3‑SAT.

The source problem (SAT) uses the format documented in ``problems.py``:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where each ``literal`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Clauses may have any length, including
zero.

The target problem (ThreeSat) requires **exactly three distinct
variables per clause**, no clause may contain both a variable and its
negation, and literals must be encoded in the same way.

The classic polynomial‑time reduction is implemented below.  It handles
all edge cases required by the specification:

* An empty formula (no clauses) is already a valid 3‑SAT instance – we
  return it unchanged.
* A clause that is empty (``[]``) makes the SAT instance unsatisfiable.
  We output a fixed unsatisfiable 3‑CNF consisting of the eight possible
  clauses over three fresh variables.  This formula is unsatisfiable
  regardless of any other clauses, satisfying the reduction.
* Unit clauses (length 1) are replaced by four 3‑clauses that force the
  original literal to be true.
* Binary clauses (length 2) are replaced by two 3‑clauses that force at
  least one of the original literals to be true.
* Clauses with three literals are left unchanged.
* Longer clauses are broken into a chain of 3‑clauses using fresh
  auxiliary variables ``y_i``.  The construction is the standard one:

      (l1 ∨ l2 ∨ y1) ∧ (¬y1 ∨ l3 ∨ y2) ∧ … ∧ (¬y_{k‑4} ∨ l_{k‑2} ∨ y_{k‑3})
      ∧ (¬y_{k‑3} ∨ l_{k‑1} ∨ l_k)

All auxiliary variables are distinct and are numbered after the original
variables, guaranteeing a polynomial increase in size.

The function ``reduce`` performs the transformation and returns a new
instance dictionary suitable for the ``ThreeSat`` problem class.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _unsat_three_sat(num_vars: int) -> Dict[str, Any]:
    """Return a fixed unsatisfiable 3‑SAT instance.

    The instance uses three variables (1, 2, 3) and contains all eight
    possible clauses over them.  For any assignment at least one clause
    is falsified, so the formula is unsatisfiable.
    """
    m = max(num_vars, 3)
    clauses: List[List[int]] = []
    for s1 in (+1, -1):
        for s2 in (+1, -1):
            for s3 in (+1, -1):
                clauses.append([s1 * 1, s2 * 2, s3 * 3])
    return {"num_vars": m, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies the ``ThreeSat`` specification and is
    satisfiable iff the input instance is satisfiable.
    """
    m: int = instance["num_vars"]
    orig_clauses: List[List[int]] = instance["clauses"]

    # Edge case: formula with no clauses – already a yes‑instance.
    if len(orig_clauses) == 0:
        return {"num_vars": m, "clauses": []}

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in orig_clauses):
        return _unsat_three_sat(m)

    new_clauses: List[List[int]] = []
    next_var = m + 1  # first fresh auxiliary variable

    for clause in orig_clauses:
        # Remove duplicate literals of the same sign and detect tautologies.
        sign_map: dict[int, int] = {}
        tautology = False
        for lit in clause:
            var = abs(lit)
            s = 1 if lit > 0 else -1
            if var in sign_map:
                if sign_map[var] != s:
                    # clause contains both a variable and its negation -> always true
                    tautology = True
                    break
                # same sign duplicate – ignore
            else:
                sign_map[var] = s
        if tautology:
            # Clause always satisfied; omit it.
            continue
        literals = [s * v for v, s in sign_map.items()]
        k = len(literals)
        if k == 0:
            # Should not happen (empty clause handled earlier), but skip.
            continue
        if k == 1:
            l = literals[0]
            a = next_var
            b = next_var + 1
            next_var += 2
            new_clauses.extend([
                [l, a, b],
                [l, a, -b],
                [l, -a, b],
                [l, -a, -b],
            ])
        elif k == 2:
            l1, l2 = literals
            a = next_var
            next_var += 1
            new_clauses.append([l1, l2, a])
            new_clauses.append([l1, l2, -a])
        elif k == 3:
            new_clauses.append(literals[:])
        else:
            # Break long clause into a chain of 3‑clauses.
            y_prev = next_var
            next_var += 1
            new_clauses.append([literals[0], literals[1], y_prev])
            for i in range(2, k - 2):
                y_curr = next_var
                next_var += 1
                new_clauses.append([-y_prev, literals[i], y_curr])
                y_prev = y_curr
            new_clauses.append([-y_prev, literals[-2], literals[-1]])

    total_vars = next_var - 1
    return {"num_vars": total_vars, "clauses": new_clauses}

