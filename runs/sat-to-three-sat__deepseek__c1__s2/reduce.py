"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction preserves satisfiability exactly:

* A source clause containing both a variable and its negation is a
  tautology, so it is dropped.
* Repeated literals in a source clause are removed.
* A source clause of length 1 is replaced by 4 three-literal clauses
  over the original literal and two fresh variables, which together
  force the original literal to be true.
* A source clause of length 2 is replaced by 2 three-literal clauses
  over the two original literals and one fresh variable.
* A source clause of length 3 is kept as is.
* A source clause of length k > 3 is split with the standard sequential
  encoding using k - 3 fresh variables.
* An empty source clause makes the formula unsatisfiable; the reduction
  returns a fixed unsatisfiable 3-SAT formula.

Every produced clause has exactly three literals on three different
variables, as required by the target problem.
"""


def _unsat_3sat():
    """A fixed unsatisfiable 3-SAT instance over variables 1, 2, 3."""
    clauses = []
    for a in (1, -1):
        for b in (2, -2):
            for c in (3, -3):
                clauses.append([a, b, c])
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # An empty clause can never be satisfied, so the whole source formula is
    # unsatisfiable.  Return a fixed unsatisfiable 3-SAT instance.
    for clause in clauses:
        if len(clause) == 0:
            return _unsat_3sat()

    next_var = num_vars + 1
    out_clauses = []

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    for clause in clauses:
        # Remove duplicate literals and detect tautologies.
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
            # Always true; dropping it preserves satisfiability.
            continue

        k = len(lits)
        if k == 0:
            # Unreachable given the empty-clause check above, but kept safe.
            return _unsat_3sat()
        elif k == 1:
            (l,) = lits
            p = fresh()
            q = fresh()
            out_clauses.append([l, p, q])
            out_clauses.append([l, p, -q])
            out_clauses.append([l, -p, q])
            out_clauses.append([l, -p, -q])
        elif k == 2:
            a, b = lits
            p = fresh()
            out_clauses.append([a, b, p])
            out_clauses.append([a, b, -p])
        elif k == 3:
            out_clauses.append([lits[0], lits[1], lits[2]])
        else:
            # Sequential (Tseitin-style) encoding of a long clause.
            ys = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out_clauses.append([-ys[i - 1], lits[i + 1], ys[i]])
            out_clauses.append([-ys[-1], lits[k - 2], lits[k - 1]])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
