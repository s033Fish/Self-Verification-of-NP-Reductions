"""Polynomial-time reduction from SAT to 3-SAT.

Source:  {"num_vars": m, "clauses": [[literal, ...], ...]}   (any clause length)
Target:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}     (exactly 3 literals
                                                              on 3 distinct vars)

Reduction outline
-----------------
Each source clause is first normalised: repeated literals are removed and a
clause containing both v and -v (a tautology) is dropped entirely.

For a normalised clause C with k distinct literals on distinct variables:
  * k == 0 : the clause is empty -> the whole formula is unsatisfiable.  We
             emit a fixed unsatisfiable 3-SAT formula over variables 1..3.
  * k == 1 : C = (l).  With two fresh vars p, q emit
                 (l v p v q), (l v -p v q), (l v p v -q), (l v -p v -q)
             which is satisfiable iff l is true.
  * k == 2 : C = (l1 v l2).  With one fresh var p emit
                 (l1 v l2 v p), (l1 v l2 v -p).
  * k == 3 : keep the clause unchanged.
  * k >= 4: standard chain with k-3 fresh vars y0..y_{k-4}:
                 (l0 v l1 v y0)
                 (-y_{i-1} v l_{i+1} v y_i)   for i = 1..k-4
                 (-y_{k-4} v l_{k-2} v l_{k-1})

All auxiliary variables are globally fresh, so every emitted clause uses three
different variables.  The construction is linear in the input size.
"""

from __future__ import annotations

from typing import Any


def _unsat_three_sat(num_vars: int) -> dict[str, Any]:
    """A fixed unsatisfiable 3-SAT instance over variables 1, 2, 3."""
    base = [1, 2, 3]
    clauses = [
        [base[i] if (mask >> i) & 1 else -base[i] for i in range(3)]
        for mask in range(8)
    ]
    return {"num_vars": max(num_vars, 3), "clauses": clauses}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    next_var = num_vars + 1
    out: list[list[int]] = []
    has_empty_clause = False

    for clause in instance["clauses"]:
        # Normalise: drop duplicates, detect tautologies.
        seen: set[int] = set()
        lits: list[int] = []
        tautology = False
        for lit in clause:
            if -lit in seen:
                tautology = True
                break
            if lit not in seen:
                seen.add(lit)
                lits.append(lit)
        if tautology:
            continue  # always satisfied, can be dropped

        k = len(lits)
        if k == 0:
            has_empty_clause = True
        elif k == 1:
            (l,) = lits
            p, q = next_var, next_var + 1
            next_var += 2
            out.append([l, p, q])
            out.append([l, -p, q])
            out.append([l, p, -q])
            out.append([l, -p, -q])
        elif k == 2:
            l1, l2 = lits
            p = next_var
            next_var += 1
            out.append([l1, l2, p])
            out.append([l1, l2, -p])
        elif k == 3:
            out.append(lits)
        else:
            aux = list(range(next_var, next_var + (k - 3)))
            next_var += k - 3
            out.append([lits[0], lits[1], aux[0]])
            for i in range(1, k - 3):
                out.append([-aux[i - 1], lits[i + 1], aux[i]])
            out.append([-aux[k - 4], lits[k - 2], lits[k - 1]])

    if has_empty_clause:
        return _unsat_three_sat(num_vars)

    return {"num_vars": next_var - 1, "clauses": out}
