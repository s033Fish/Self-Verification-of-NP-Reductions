"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction is the standard equisatisfiable clause-length normalization:

* A clause that is a tautology (contains both v and -v) can be dropped.
* Repeated literals inside a clause can be removed.
* An empty clause makes the formula unsatisfiable; we emit a fixed
  unsatisfiable 3-SAT formula on three variables.
* A unit clause [l] is replaced, using two fresh variables a, b, by
      (l v a v b), (l v -a v b), (l v a v -b), (l v -a v -b),
  which together force l to be true.
* A 2-clause [l1, l2] is replaced, using one fresh variable a, by
      (l1 v l2 v a), (l1 v l2 v -a),
  which is equivalent to l1 v l2.
* A 3-clause is already a valid 3-SAT clause.
* A clause (l1 v ... v lk), k >= 4, is replaced by the chain
      (l1 v l2 v a1),
      (-a1 v l3 v a2),
      ...
      (-a_{k-3} v l_{k-1} v lk),
  with fresh a_i.  This is satisfiable exactly when the original clause is.

All auxiliary variables are fresh, so the resulting 3-SAT instance is
satisfiable exactly when the input SAT instance is.  The running time is
linear in the total number of literals.
"""


def reduce(instance):
    """Reduce a SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    source_clauses = instance["clauses"]

    # Normalize: remove duplicate literals, drop tautological clauses.
    normalized = []
    for clause in source_clauses:
        seen = set()
        literals = []
        tautology = False
        for literal in clause:
            if literal in seen:
                continue
            if -literal in seen:
                tautology = True
                break
            seen.add(literal)
            literals.append(literal)
        if not tautology:
            normalized.append(literals)

    # An empty clause is unsatisfiable.  Emit a fixed unsatisfiable 3-SAT
    # formula (all 8 clauses over three variables).
    if any(len(clause) == 0 for clause in normalized):
        fixed_num_vars = max(num_vars, 3)
        return {
            "num_vars": fixed_num_vars,
            "clauses": [
                [1, 2, 3],
                [1, 2, -3],
                [1, -2, 3],
                [1, -2, -3],
                [-1, 2, 3],
                [-1, 2, -3],
                [-1, -2, 3],
                [-1, -2, -3],
            ],
        }

    next_var = num_vars

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    target_clauses = []

    for clause in normalized:
        length = len(clause)

        if length == 3:
            # Already a valid 3-SAT clause (after dedup, the three
            # variables are distinct; a complementary pair would have
            # been detected as a tautology above).
            target_clauses.append(list(clause))

        elif length == 1:
            (literal,) = clause
            a = fresh()
            b = fresh()
            target_clauses.append([literal, a, b])
            target_clauses.append([literal, -a, b])
            target_clauses.append([literal, a, -b])
            target_clauses.append([literal, -a, -b])

        elif length == 2:
            first, second = clause
            a = fresh()
            target_clauses.append([first, second, a])
            target_clauses.append([first, second, -a])

        else:
            # length >= 4: chain the literals with fresh variables.
            previous = fresh()
            target_clauses.append([clause[0], clause[1], previous])
            for index in range(2, length - 2):
                current = fresh()
                target_clauses.append([-previous, clause[index], current])
                previous = current
            target_clauses.append([-previous, clause[length - 2], clause[length - 1]])

    return {"num_vars": next_var, "clauses": target_clauses}
