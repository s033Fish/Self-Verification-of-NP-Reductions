"""Polynomial-time reduction from SAT to 3-SAT.

Source instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance:  {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

The reduction preserves satisfiability exactly:

  * A tautological clause (containing both v and -v) is always true, so it
    is removed.
  * Repeated literals in a clause are removed.
  * An empty clause is unsatisfiable; we emit a fixed unsatisfiable 3-CNF.
  * A unit clause [l] becomes four clauses over fresh x, y:
        (l v x v y), (l v x v -y), (l v -x v y), (l v -x v -y)
    which together are satisfiable iff l is true.
  * A binary clause [l1, l2] becomes two clauses over fresh x:
        (l1 v l2 v x), (l1 v l2 v -x)
    which together are satisfiable iff l1 v l2 is true.
  * A ternary clause is already a valid 3-SAT clause.
  * A clause (l1 v ... v lk), k >= 4, becomes the standard chain using fresh
    y1..y_{k-3}:
        (l1 v l2 v y1),
        (-y1 v l3 v y2), ..., (-y_{k-4} v l_{k-2} v y_{k-3}),
        (-y_{k-3} v l_{k-1} v lk)
    which is satisfiable iff the original clause is.

Fresh variables are numbered after the original ones, so the construction uses
O(total literals) variables and clauses and runs in linear time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    fresh = num_vars

    def new_var():
        nonlocal fresh
        fresh += 1
        return fresh

    out = []
    has_empty_clause = False

    for clause in clauses:
        # Simplify: drop tautologies and duplicate literals.
        seen = set()
        lits = []
        tautology = False
        for lit in clause:
            if -lit in seen:
                tautology = True
                break
            if lit not in seen:
                seen.add(lit)
                lits.append(lit)
        if tautology:
            continue

        k = len(lits)
        if k == 0:
            has_empty_clause = True
            break
        if k == 1:
            (l,) = lits
            x = new_var()
            y = new_var()
            out.append([l, x, y])
            out.append([l, x, -y])
            out.append([l, -x, y])
            out.append([l, -x, -y])
        elif k == 2:
            l1, l2 = lits
            x = new_var()
            out.append([l1, l2, x])
            out.append([l1, l2, -x])
        elif k == 3:
            out.append(lits)
        else:
            ys = [new_var() for _ in range(k - 3)]
            out.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out.append([-ys[i - 1], lits[i + 1], ys[i]])
            out.append([-ys[-1], lits[k - 2], lits[k - 1]])

    if has_empty_clause:
        # All eight clauses on variables 1, 2, 3: unsatisfiable.
        unsat_clauses = [
            [a, b, c]
            for a in (1, -1)
            for b in (2, -2)
            for c in (3, -3)
        ]
        return {"num_vars": 3, "clauses": unsat_clauses}

    if not out:
        # No clauses (possibly after dropping tautologies): satisfiable.
        return {"num_vars": num_vars, "clauses": []}

    # 3-SAT requires at least 3 variables when clauses are present.
    return {"num_vars": max(fresh, 3), "clauses": out}
