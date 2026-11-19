"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

For every source clause we produce an equisatisfiable set of 3-clauses over
the original variables plus fresh variables.  Fresh variables are never shared
between source clauses, so they can be chosen freely per clause.

  * tautological clauses (containing both v and -v) are dropped;
  * duplicate literals inside a clause are removed;
  * []            -> the 8-clause contradiction on 3 fresh variables;
  * [l]           -> the 4 clauses that force l true:
                     (l v a v b) (l v ~a v b) (l v a v ~b) (l v ~a v ~b);
  * [l1, l2]      -> (l1 v l2 v a) ^ (l1 v l2 v ~a), forcing l1 v l2;
  * [l1, l2, l3]  -> unchanged;
  * [l1..lk], k>3 -> chain of k-2 clauses using k-3 fresh variables:
        (l1 v l2 v y1) ^ (~y1 v l3 v y2) ^ ... ^ (~y_{k-3} v l_{k-1} v lk)
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars + 1

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    unsatisfiable = False

    for clause in clauses:
        # De-duplicate literals and detect tautologies (v and -v together).
        seen = set()
        lits = []
        tautology = False
        for lit in clause:
            if lit in seen:
                continue
            if -lit in seen:
                tautology = True
                break
            seen.add(lit)
            lits.append(lit)
        if tautology:
            continue

        k = len(lits)
        if k == 0:
            unsatisfiable = True
        elif k == 1:
            l = lits[0]
            a, b = fresh(), fresh()
            out_clauses.append([l, a, b])
            out_clauses.append([l, -a, b])
            out_clauses.append([l, a, -b])
            out_clauses.append([l, -a, -b])
        elif k == 2:
            l1, l2 = lits
            a = fresh()
            out_clauses.append([l1, l2, a])
            out_clauses.append([l1, l2, -a])
        elif k == 3:
            out_clauses.append(list(lits))
        else:
            ys = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out_clauses.append([-ys[i - 1], lits[i + 1], ys[i]])
            out_clauses.append([-ys[k - 4], lits[k - 2], lits[k - 1]])

    if unsatisfiable:
        a, b, c = fresh(), fresh(), fresh()
        for s1 in (a, -a):
            for s2 in (b, -b):
                for s3 in (c, -c):
                    out_clauses.append([s1, s2, s3])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
