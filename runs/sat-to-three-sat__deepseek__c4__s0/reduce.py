"""Polynomial-time reduction from SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Construction (Tseitin-style with fresh variables):

For each source clause:
  * Drop duplicate literals and drop the clause entirely if it is a
    tautology (contains both v and -v): such a clause is always true.
  * Let the remaining distinct literals be l1..lk.
      k == 0 : the clause is empty -> the formula is unsatisfiable.
      k == 1 : [l1]  -> [l1,p,q], [l1,p,-q], [l1,-p,q], [l1,-p,-q]
      k == 2 : [l1,l2] -> [l1,l2,p], [l1,l2,-p]
      k == 3 : keep [l1,l2,l3]
      k > 3  : fresh y1..y_{k-3} with the chain
               [l1,l2,y1], [-y1,l3,y2], ..., [-y_{k-4},l_{k-2},y_{k-3}],
               [-y_{k-3},l_{k-1},l_k]
  Fresh variables are numbered m+1, m+2, ... and are all distinct from the
  source variables and from each other, so every produced clause has three
  literals on three different variables.

If any source clause is empty, the whole formula is unsatisfiable; we then
emit all 8 clauses over 3 fresh variables, which is unsatisfiable.

The reduction is satisfiability-preserving and runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    m = instance["num_vars"]
    clauses = instance["clauses"]

    fresh = m
    out_clauses: list[list[int]] = []
    unsat = False

    def new_var() -> int:
        nonlocal fresh
        fresh += 1
        return fresh

    for clause in clauses:
        lits: list[int] = []
        seen: set[int] = set()
        tautology = False
        for lit in clause:
            if -lit in seen:
                tautology = True
                break
            if lit not in seen:
                seen.add(lit)
                lits.append(lit)
        if tautology:
            # Always satisfied; safe to drop.
            continue

        k = len(lits)
        if k == 0:
            unsat = True
            continue
        if k == 1:
            (l,) = lits
            p = new_var()
            q = new_var()
            out_clauses.append([l, p, q])
            out_clauses.append([l, p, -q])
            out_clauses.append([l, -p, q])
            out_clauses.append([l, -p, -q])
        elif k == 2:
            l1, l2 = lits
            p = new_var()
            out_clauses.append([l1, l2, p])
            out_clauses.append([l1, l2, -p])
        elif k == 3:
            out_clauses.append([lits[0], lits[1], lits[2]])
        else:
            ys = [new_var() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out_clauses.append([-ys[i - 1], lits[i + 1], ys[i]])
            out_clauses.append([-ys[-1], lits[k - 2], lits[k - 1]])

    if unsat:
        a = new_var()
        b = new_var()
        c = new_var()
        for sa in (a, -a):
            for sb in (b, -b):
                for sc in (c, -c):
                    out_clauses.append([sa, sb, sc])

    return {"num_vars": fresh, "clauses": out_clauses}
