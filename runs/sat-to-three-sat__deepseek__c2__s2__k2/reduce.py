"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction is equisatisfiable and produces a valid 3-SAT instance:
every output clause has exactly 3 literals on 3 distinct variables.

Steps:
  * Simplify each clause: remove duplicate literals and drop tautological
    clauses (those containing both v and -v), since a tautology is always
    satisfied and can be removed without changing satisfiability.
  * If any clause is empty, the formula is unsatisfiable; return a fixed
    unsatisfiable 3-SAT formula over 3 variables (all 8 clauses).
  * Otherwise transform each non-empty clause C = (l1 v ... v lk):
      - k == 1: (l1 v x v y) & (l1 v x v -y) & (l1 v -x v y) & (l1 v -x v -y)
        with fresh x, y.  This is equivalent to (l1).
      - k == 2: (l1 v l2 v x) & (l1 v l2 v -x) with fresh x.
        This is equivalent to (l1 v l2).
      - k == 3: keep the clause as is.
      - k >= 4: Tseitin chain
          (l1 v l2 v x1) & (-x1 v l3 v x2) & ... & (-x_{k-3} v l_{k-1} v lk)
        with fresh x_i.  This is equisatisfiable with C.

All fresh variables are strictly greater than the original num_vars, so no
collisions occur.  The output num_vars is the largest variable used.
"""


def _unsat_three_sat():
    """A fixed unsatisfiable 3-SAT instance: all 8 clauses over vars 1,2,3."""
    clauses = [
        [1, 2, 3],
        [-1, 2, 3],
        [1, -2, 3],
        [1, 2, -3],
        [-1, -2, 3],
        [-1, 2, -3],
        [1, -2, -3],
        [-1, -2, -3],
    ]
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Simplify clauses: dedupe literals, drop tautologies.
    simplified = []
    for clause in clauses:
        seen = set()
        literals = []
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                literals.append(literal)
        if tautology:
            continue
        simplified.append(literals)

    # An empty clause makes the formula unsatisfiable.
    if any(len(clause) == 0 for clause in simplified):
        return _unsat_three_sat()

    fresh = num_vars + 1
    out = []

    for clause in simplified:
        k = len(clause)
        if k == 1:
            l1 = clause[0]
            x = fresh
            y = fresh + 1
            fresh += 2
            out.append([l1, x, y])
            out.append([l1, x, -y])
            out.append([l1, -x, y])
            out.append([l1, -x, -y])
        elif k == 2:
            l1, l2 = clause
            x = fresh
            fresh += 1
            out.append([l1, l2, x])
            out.append([l1, l2, -x])
        elif k == 3:
            out.append([clause[0], clause[1], clause[2]])
        else:
            # k >= 4: Tseitin chain with k-3 fresh variables.
            xs = list(range(fresh, fresh + (k - 3)))
            fresh += (k - 3)
            out.append([clause[0], clause[1], xs[0]])
            for i in range(1, k - 3):
                out.append([-xs[i - 1], clause[i + 1], xs[i]])
            out.append([-xs[-1], clause[k - 2], clause[k - 1]])

    if out:
        target_num_vars = fresh - 1
    else:
        target_num_vars = num_vars

    return {"num_vars": target_num_vars, "clauses": out}
