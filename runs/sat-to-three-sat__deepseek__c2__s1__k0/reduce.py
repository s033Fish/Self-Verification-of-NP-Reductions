"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

Source instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance:  {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Construction (all fresh variables are globally unique):

  * A clause containing both v and -v is a tautology and is dropped.
  * Repeated literals are removed.
  * Length 3  -> kept as is (after normalization the 3 variables are
                 distinct and no complementary pair remains).
  * Length 2  -> (l1 v l2) becomes (l1 v l2 v y) and (l1 v l2 v -y)
                 with one fresh y.  This is equisatisfiable.
  * Length 1  -> (l) becomes the four clauses
                 (l v y1 v y2), (l v -y1 v y2), (l v y1 v -y2),
                 (l v -y1 v -y2) with fresh y1, y2, which forces l true.
  * Length k>=4 -> chain splitting with fresh y1..y_{k-3}:
                 (l1 v l2 v y1),
                 (-y1 v l3 v y2), ..., (-y_{k-4} v l_{k-2} v y_{k-3}),
                 (-y_{k-3} v l_{k-1} v lk).
  * An empty clause makes the source unsatisfiable; we return a fixed
    unsatisfiable 3-SAT formula (all 8 clauses over three variables).

The number of fresh variables is linear in the input size, so the
reduction runs in polynomial time.
"""


def _unsatisfiable_three_sat(num_vars):
    """All eight 3-clauses over variables 1, 2, 3: unsatisfiable."""
    clauses = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            for s3 in (1, -1):
                clauses.append([s1 * 1, s2 * 2, s3 * 3])
    return {"num_vars": max(num_vars, 3), "clauses": clauses}


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # An empty clause can never be satisfied: the source is unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return _unsatisfiable_three_sat(num_vars)

    next_var = num_vars

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    out = []
    for clause in clauses:
        # Normalize: drop duplicates, detect tautologies (v and -v).
        seen = set()
        lits = []
        tautology = False
        for literal in clause:
            if literal in seen:
                continue
            if -literal in seen:
                tautology = True
                break
            seen.add(literal)
            lits.append(literal)
        if tautology:
            # Always satisfied; contributes no constraint.
            continue

        k = len(lits)
        if k == 1:
            (l,) = lits
            y1 = fresh()
            y2 = fresh()
            out.append([l, y1, y2])
            out.append([l, -y1, y2])
            out.append([l, y1, -y2])
            out.append([l, -y1, -y2])
        elif k == 2:
            l1, l2 = lits
            y = fresh()
            out.append([l1, l2, y])
            out.append([l1, l2, -y])
        elif k == 3:
            out.append([lits[0], lits[1], lits[2]])
        else:
            # k >= 4: chain of 3-clauses with k - 3 fresh variables.
            ys = [fresh() for _ in range(k - 3)]
            out.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out.append([-ys[i - 1], lits[i + 1], ys[i]])
            out.append([-ys[-1], lits[k - 2], lits[k - 1]])

    return {"num_vars": next_var, "clauses": out}
