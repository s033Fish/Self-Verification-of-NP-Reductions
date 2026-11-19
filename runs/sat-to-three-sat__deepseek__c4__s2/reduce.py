"""Polynomial-time reduction from SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

The reduction is the standard clause-splitting construction:

  * Drop tautological clauses (containing both v and -v) and duplicate
    literals within a clause.
  * A clause of length 0 makes the formula unsatisfiable; emit a fixed
    unsatisfiable 3-CNF (all 8 clauses over 3 variables).
  * Length 1: (l) -> (l v a v b) & (l v a v -b) & (l v -a v b) & (l v -a v -b)
  * Length 2: (l1 v l2) -> (l1 v l2 v a) & (l1 v l2 v -a)
  * Length 3: keep as is.
  * Length k >= 4: introduce k-3 fresh variables a_1..a_{k-3} and emit
        (l1 v l2 v a1)
        (-a1 v l3 v a2)
        ...
        (-a_{k-3} v l_{k-1} v l_k)

Every emitted clause has exactly 3 literals on 3 distinct variables.
"""

from __future__ import annotations


def _dedup_clause(clause):
    """Remove duplicate literals; return None if the clause is a tautology."""
    seen = set()
    out = []
    for lit in clause:
        if lit in seen:
            continue
        if -lit in seen:
            return None  # tautology, always satisfied
        seen.add(lit)
        out.append(lit)
    return out


def _unsat_3cnf(num_vars):
    """A fixed unsatisfiable 3-CNF over variables 1, 2, 3."""
    clauses = []
    for s1 in (1, -1):
        for s2 in (2, -2):
            for s3 in (3, -3):
                clauses.append([s1, s2, s3])
    return {"num_vars": max(num_vars, 3), "clauses": clauses}


def reduce(instance):
    num_vars = instance["num_vars"]
    raw_clauses = instance["clauses"]

    # Preprocess: drop tautologies, remove duplicate literals.
    clauses = []
    for clause in raw_clauses:
        simplified = _dedup_clause(clause)
        if simplified is None:
            continue  # tautology
        if len(simplified) == 0:
            # Empty clause: the whole formula is unsatisfiable.
            return _unsat_3cnf(num_vars)
        clauses.append(simplified)

    next_var = num_vars + 1
    out_clauses = []

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    for lits in clauses:
        k = len(lits)
        if k == 3:
            out_clauses.append([lits[0], lits[1], lits[2]])
        elif k == 2:
            a = fresh()
            out_clauses.append([lits[0], lits[1], a])
            out_clauses.append([lits[0], lits[1], -a])
        elif k == 1:
            a = fresh()
            b = fresh()
            l = lits[0]
            out_clauses.append([l, a, b])
            out_clauses.append([l, a, -b])
            out_clauses.append([l, -a, b])
            out_clauses.append([l, -a, -b])
        else:  # k >= 4
            aux = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], aux[0]])
            for i in range(1, k - 3):
                out_clauses.append([-aux[i - 1], lits[i + 1], aux[i]])
            out_clauses.append([-aux[-1], lits[k - 2], lits[k - 1]])

    target_num_vars = next_var - 1
    # A 3-CNF with clauses needs at least 3 variables (all clauses already
    # use 3 distinct variables, so this is normally automatic).
    if out_clauses:
        target_num_vars = max(target_num_vars, 3)
    else:
        target_num_vars = num_vars

    return {"num_vars": target_num_vars, "clauses": out_clauses}
