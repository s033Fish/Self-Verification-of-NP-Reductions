"""Reduction from SAT to 3‑SAT.

The source problem (``Sat``) allows clauses of arbitrary length, including
empty clauses.  The target problem (``ThreeSat``) requires every clause to
contain exactly three *different* variables, none of which appear both
positively and negatively in the same clause.

The reduction follows the classic textbook construction:

* An empty clause makes the whole formula unsatisfiable.  We replace the
  entire instance by a fixed unsatisfiable 3‑SAT instance consisting of the
  eight possible clauses over three fresh variables.  This instance is
  unsatisfiable because each of the eight possible assignments falsifies one
  of the clauses.

* A formula with no clauses is trivially satisfiable.  We return the empty
  3‑SAT instance (zero clauses, zero variables).

* For a clause of length 1 (unit clause) we use four auxiliary clauses that
  force the unit literal to be true while respecting the 3‑SAT format:

```
    (l ∨ a ∨ b) ∧ (l ∨ a ∨ ¬b) ∧ (l ∨ ¬a ∨ b) ∧ (l ∨ ¬a ∨ ¬b)
```
  The four clauses are satisfied iff ``l`` is satisfied.

* For a clause of length 2 we introduce a fresh variable ``a`` and add the
  two clauses ``(l1 ∨ l2 ∨ a)`` and ``(l1 ∨ l2 ∨ ¬a)``.  This is equivalent to
  the original 2‑literal clause.

* For a clause of length ≥ 3 we break it into a chain of 3‑literal clauses
  using fresh variables ``y_i`` as described in standard reductions.

All fresh variables are numbered starting after the original ``num_vars``
so they are guaranteed to be distinct from the original ones.  The function
runs in time linear in the size of the input (polynomial by definition).
"""

from __future__ import annotations

from typing import List, Dict, Any


def _unsat_three_sat_instance() -> Dict[str, Any]:
    """Return a fixed unsatisfiable 3‑SAT instance.

    The instance uses three variables (1, 2, 3) and contains all eight
    possible clauses of size three.  For any assignment exactly one clause is
    falsified, making the whole formula unsatisfiable.
    """
    vars_ = [1, 2, 3]
    clauses: List[List[int]] = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            for s3 in (1, -1):
                clauses.append([s1 * vars_[0], s2 * vars_[1], s3 * vars_[2]])
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance is satisfiable iff the input instance is
    satisfiable.  The transformation runs in polynomial time.
    """
    num_vars: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: any empty clause makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            return _unsat_three_sat_instance()

    # Edge case: no clauses -> trivially satisfiable.
    if not clauses:
        return {"num_vars": 0, "clauses": []}

    new_clauses: List[List[int]] = []
    fresh = num_vars + 1  # next fresh variable index

    for cl in clauses:
        # Remove duplicate literals and detect tautologies (v and -v).
        lit_set = set()
        tautology = False
        for lit in cl:
            if -lit in lit_set:
                tautology = True
                break
            lit_set.add(lit)
        if tautology:
            # Clause always true, can be omitted.
            continue
        cleaned = list(lit_set)
        k = len(cleaned)
        if k == 0:
            return _unsat_three_sat_instance()
        if k == 1:
            l = cleaned[0]
            a = fresh
            b = fresh + 1
            fresh += 2
            new_clauses.append([l, a, b])
            new_clauses.append([l, a, -b])
            new_clauses.append([l, -a, b])
            new_clauses.append([l, -a, -b])
        elif k == 2:
            l1, l2 = cleaned
            a = fresh
            fresh += 1
            new_clauses.append([l1, l2, a])
            new_clauses.append([l1, l2, -a])
        else:
            # k >= 3
            if k == 3:
                new_clauses.append([cleaned[0], cleaned[1], cleaned[2]])
                continue
            # Chain construction for longer clauses.
            y_prev = fresh
            fresh += 1
            new_clauses.append([cleaned[0], cleaned[1], y_prev])
            for i in range(2, k - 2):
                y_curr = fresh
                fresh += 1
                new_clauses.append([-y_prev, cleaned[i], y_curr])
                y_prev = y_curr
            new_clauses.append([-y_prev, cleaned[-2], cleaned[-1]])

    total_vars = fresh - 1
    # ThreeSat requires at least three variables when there is at least one clause.
    if new_clauses and total_vars < 3:
        total_vars = 3
    return {"num_vars": total_vars, "clauses": new_clauses}

