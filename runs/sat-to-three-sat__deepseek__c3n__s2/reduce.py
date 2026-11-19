"""Polynomial-time reduction from SAT to 3-SAT.

Source (SAT): {"num_vars": m, "clauses": [[literal, ...], ...]}
Target (3-SAT): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

The reduction:
  1. Normalise every clause: drop duplicate literals.  A clause that
     contains both v and -v is a tautology and is dropped entirely.
  2. An empty clause makes the formula unsatisfiable; we emit a fixed
     unsatisfiable 3-SAT formula over 3 variables.
  3. Clauses of length 1, 2, >=4 are converted with fresh variables:
       [l]        -> (l v y v z)(l v ~y v z)(l v y v ~z)(l v ~y v ~z)
       [l1, l2]   -> (l1 v l2 v y)(l1 v l2 v ~y)
       [l1..lk]   -> (l1 v l2 v y1)(~y1 v l3 v y2)...(~y_{k-3} v l_{k-1} v lk)
     A clause of length 3 (on 3 distinct variables after normalisation)
     is kept as is.

Every produced clause has exactly 3 literals on 3 distinct variables, and
the number of new variables is linear in the input size.
"""

from __future__ import annotations


def _unsat_formula(num_vars: int) -> dict:
    """All 8 clauses over variables 1,2,3: unsatisfiable."""
    clauses = []
    for a in (1, -1):
        for b in (2, -2):
            for c in (3, -3):
                clauses.append([a, b, c])
    return {"num_vars": max(num_vars, 3), "clauses": clauses}


def reduce(instance: dict) -> dict:
    m = instance["num_vars"]
    raw_clauses = instance["clauses"]

    # --- Step 1: normalise clauses -------------------------------------
    simplified = []
    for clause in raw_clauses:
        lits = set(clause)
        if any(-lit in lits for lit in lits):
            # tautology: always satisfied, drop it
            continue
        if not lits:
            # empty clause: formula is unsatisfiable
            return _unsat_formula(m)
        simplified.append(list(lits))

    # --- Step 2: expand each clause ------------------------------------
    next_var = m + 1
    out = []

    for clause in simplified:
        k = len(clause)
        if k == 1:
            (l,) = clause
            y = next_var
            z = next_var + 1
            next_var += 2
            out.append([l, y, z])
            out.append([l, -y, z])
            out.append([l, y, -z])
            out.append([l, -y, -z])
        elif k == 2:
            l1, l2 = clause
            y = next_var
            next_var += 1
            out.append([l1, l2, y])
            out.append([l1, l2, -y])
        elif k == 3:
            out.append(list(clause))
        else:  # k >= 4
            ys = list(range(next_var, next_var + (k - 3)))
            next_var += k - 3
            out.append([clause[0], clause[1], ys[0]])
            for i in range(1, k - 3):
                out.append([-ys[i - 1], clause[i + 1], ys[i]])
            out.append([-ys[-1], clause[k - 2], clause[k - 1]])

    num_vars = next_var - 1
    if out:
        num_vars = max(num_vars, 3)
    return {"num_vars": num_vars, "clauses": out}
