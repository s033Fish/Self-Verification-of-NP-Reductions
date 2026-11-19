"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction works clause by clause:

* A tautological clause (one containing both v and -v) is always satisfied,
  so it is dropped.
* Repeated literals inside a clause are removed.
* A clause of exactly 3 literals is emitted unchanged.
* A clause of 2 literals (l1 or l2) is padded with one fresh variable x:
      (l1 or l2 or x) and (l1 or l2 or not x)
  which is satisfiable iff (l1 or l2) is.
* A clause of 1 literal (l) is padded with two fresh variables x, y:
      (l or x or y), (l or not x or y), (l or x or not y), (l or not x or not y)
  which is satisfiable iff l is true.
* A clause l0 or ... or l_{k-1} with k >= 4 is replaced by a chain using
  fresh variables x0..x_{k-4}:
      (l0 or l1 or x0)
      (not x0 or l2 or x1)
      ...
      (not x_{k-4} or l_{k-2} or l_{k-1})
  which is satisfiable iff the original clause is.
* An empty clause is unsatisfiable, so the whole formula is mapped to the
  unsatisfiable 3-CNF formula consisting of all 8 clauses over 3 variables.

All fresh variables are numbered after the original variables, so the result
is a valid 3-SAT instance.  The number of new clauses and variables is linear
in the size of the input, hence the reduction runs in polynomial time.
"""

from itertools import product


def _unsat_gadget():
    """All 8 clauses over variables 1, 2, 3: an unsatisfiable 3-SAT instance."""
    clauses = []
    for signs in product((1, -1), repeat=3):
        clauses.append([sign * var for sign, var in zip(signs, (1, 2, 3))])
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance):
    """Reduce a SAT instance to a 3-SAT instance (yes-preserving)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # An empty clause makes the formula unsatisfiable; emit an unsat gadget.
    for clause in clauses:
        if len(clause) == 0:
            return _unsat_gadget()

    next_var = num_vars + 1
    out_clauses = []

    for clause in clauses:
        # Remove duplicates and detect tautologies (v and -v together).
        literals = []
        seen = set()
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                literals.append(literal)

        if tautology:
            # Always satisfied; contributes no constraint.
            continue

        k = len(literals)

        if k == 0:
            # Should have been caught above, but keep it safe.
            return _unsat_gadget()

        if k == 1:
            (lit,) = literals
            x = next_var
            y = next_var + 1
            next_var += 2
            out_clauses.append([lit, x, y])
            out_clauses.append([lit, -x, y])
            out_clauses.append([lit, x, -y])
            out_clauses.append([lit, -x, -y])

        elif k == 2:
            l1, l2 = literals
            x = next_var
            next_var += 1
            out_clauses.append([l1, l2, x])
            out_clauses.append([l1, l2, -x])

        elif k == 3:
            out_clauses.append([literals[0], literals[1], literals[2]])

        else:
            # Chain encoding for k >= 4.
            aux = list(range(next_var, next_var + (k - 3)))
            next_var += k - 3

            out_clauses.append([literals[0], literals[1], aux[0]])
            for i in range(1, k - 3):
                out_clauses.append([-aux[i - 1], literals[i + 1], aux[i]])
            out_clauses.append([-aux[k - 4], literals[k - 2], literals[k - 1]])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
