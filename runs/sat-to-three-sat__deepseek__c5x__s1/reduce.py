"""Polynomial-time reduction from SAT to 3-SAT.

Given a CNF formula with clauses of arbitrary length, produce an equivalent
3-CNF formula (exactly 3 literals per clause, on 3 different variables).

Gadgets:
  * tautological clause (contains v and -v): dropped.
  * empty clause: 8 clauses over 3 fresh vars enumerating all assignments,
    which is unsatisfiable.
  * 1-literal clause (l): (l v y v z) ^ (l v y v ~z) ^ (l v ~y v z)
    ^ (l v ~y v ~z)  ==  l, using fresh y, z.
  * 2-literal clause (l1 v l2): (l1 v l2 v y) ^ (l1 v l2 v ~y) == l1 v l2.
  * 3-literal clause: kept as is.
  * k>3 literals: standard chain with k-3 fresh variables.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    counter = [num_vars]
    out = []

    def fresh():
        counter[0] += 1
        return counter[0]

    def add_unsat_gadget():
        a, b, c = fresh(), fresh(), fresh()
        for la in (a, -a):
            for lb in (b, -b):
                for lc in (c, -c):
                    out.append([la, lb, lc])

    for clause in clauses:
        # Simplify: drop duplicate literals; a clause containing both v and
        # -v is a tautology and can be removed entirely.
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
            add_unsat_gadget()
        elif k == 1:
            (l,) = lits
            y, z = fresh(), fresh()
            out.append([l, y, z])
            out.append([l, y, -z])
            out.append([l, -y, z])
            out.append([l, -y, -z])
        elif k == 2:
            l1, l2 = lits
            y = fresh()
            out.append([l1, l2, y])
            out.append([l1, l2, -y])
        elif k == 3:
            out.append([lits[0], lits[1], lits[2]])
        else:
            y_prev = fresh()
            out.append([lits[0], lits[1], y_prev])
            for i in range(2, k - 2):
                y_next = fresh()
                out.append([-y_prev, lits[i], y_next])
                y_prev = y_next
            out.append([-y_prev, lits[k - 2], lits[k - 1]])

    return {"num_vars": counter[0], "clauses": out}
