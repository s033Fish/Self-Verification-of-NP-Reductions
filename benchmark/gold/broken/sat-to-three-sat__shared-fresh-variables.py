"""BROKEN: SAT -> 3-SAT whose long-clause chains all share ONE variable y.                         [test, famous]

SOURCE  SAT    {"num_vars": m, "clauses": [[literal, ...], ...]}  any clause lengths
TARGET  3-SAT  {"num_vars": m', "clauses": [[l1, l2, l3], ...]}   3 different variables per clause

Construction, clause by clause (fresh variables are new for every clause):
  0. Clean up: remove repeated literals; drop a clause that contains both v
     and -v (it is always true). An empty clause makes the formula
     unsatisfiable: return a fixed unsatisfiable 3-SAT instance (all 8
     sign patterns on variables 1, 2, 3).
  1. One literal (l): with fresh a, b:
       (l, a, b) (l, a, -b) (l, -a, b) (l, -a, -b)
     All four hold iff l is true.
  2. Two literals (l1, l2): with fresh a:  (l1, l2, a) (l1, l2, -a)
  3. Three literals: unchanged (already 3 different variables after step 0).
  4. k > 3 literals: with fresh y1..y_{k-3}, the chain
       (l1, l2, y1) (-y1, l3, y2) ... (-y_{k-3}, l_{k-1}, l_k)
     satisfiable by some y exactly when some l_i is true.

Why: each step preserves satisfiability for every assignment of the original
variables (the fresh ones can always be chosen to fit), so the whole
formula is satisfiable iff the source is.

Edge cases: no clauses stays no clauses (yes for any m). Every output clause
has 3 different variables, so m' >= 3 whenever there are clauses.
"""

UNSATISFIABLE = {
    "num_vars": 3,
    "clauses": [[a * 1, b * 2, c * 3] for a in (1, -1) for b in (1, -1) for c in (1, -1)],
}


def reduce(instance):
    m = instance["num_vars"]
    out = []
    next_var = m + 1

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var - 1

    shared = []
    for clause in instance["clauses"]:
        literals = list(dict.fromkeys(clause))  # drop repeats, keep order
        if any(-l in literals for l in literals):
            continue  # always true
        if not literals:
            return {"num_vars": UNSATISFIABLE["num_vars"],
                    "clauses": [list(c) for c in UNSATISFIABLE["clauses"]]}
        if len(literals) == 1:
            (l,) = literals
            a, b = fresh(), fresh()
            out += [[l, a, b], [l, a, -b], [l, -a, b], [l, -a, -b]]
        elif len(literals) == 2:
            l1, l2 = literals
            a = fresh()
            out += [[l1, l2, a], [l1, l2, -a]]
        elif len(literals) == 3:
            out.append(literals)
        else:
            # BUG: every clause of length >= 4 reuses the same chain variables
            if not shared:
                shared.extend(fresh() for _ in range(len(literals)))
            while len(shared) < len(literals) - 3:
                shared.append(fresh())
            y = shared[0]
            out.append([literals[0], literals[1], y])
            for i, l in enumerate(literals[2:-2], start=1):
                y_next = shared[i]
                out.append([-y, l, y_next])
                y = y_next
            out.append([-y, literals[-2], literals[-1]])
    return {"num_vars": next_var - 1, "clauses": out}