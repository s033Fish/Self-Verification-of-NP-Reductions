"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction
------------
Let n = num_vars and k = len(clauses).  Choose a base b = max(6, k + 1),
large enough that every digit of every number and of the target is < b, so
adding the chosen numbers never produces a carry between digit positions.

Use k low-order digit positions, one per clause, and n higher positions, one
per variable.  For each variable i:

  * T_i has digit 1 in variable position i, plus digit 1 in clause position j
    for every clause j that contains the literal +i.
  * F_i has digit 1 in variable position i, plus digit 1 in clause position j
    for every clause j that contains the literal -i.

For each clause j add two slack numbers, each with digit 1 only in clause
position j.

The target has digit 1 in every variable position and digit 3 in every clause
position.

Why it works
------------
Every number contributes at most 1 to any variable digit, so the target's 1
there forces choosing exactly one of T_i, F_i for each i.  This is a total
truth assignment.  A clause digit receives one unit for each true literal in
that clause plus one unit for each of its two slacks chosen.  It reaches the
target value 3 exactly when at least one literal in the clause is true (with
0 true literals at most 2 can be supplied; with 1, 2, or 3 true literals the
slacks fill the remainder).  Hence a subset sums to the target iff the
formula is satisfiable.

The reduction uses 2n + 2k numbers, each with O(n + k) digits, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Subset Sum instance (yes iff yes)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # Base strictly greater than the largest possible digit sum (3 true
    # literals + 2 slacks = 5), so no carries occur.
    base = max(6, k + 1)

    numbers = []

    # One true-number and one false-number per variable.
    for i in range(1, num_vars + 1):
        var_pos = k + (i - 1)
        true_value = base ** var_pos
        false_value = base ** var_pos
        for j, clause in enumerate(clauses):
            if i in clause:
                true_value += base ** j
            if -i in clause:
                false_value += base ** j
        numbers.append(true_value)
        numbers.append(false_value)

    # Two slack numbers per clause, each able to fill one unit of the
    # clause's digit.
    for j in range(k):
        numbers.append(base ** j)
        numbers.append(base ** j)

    # Target: exactly one selected literal-number per variable, and exactly
    # three units per clause (at least one true literal plus slacks).
    target = 0
    for i in range(1, num_vars + 1):
        target += base ** (k + (i - 1))
    for j in range(k):
        target += 3 * (base ** j)

    return {"numbers": numbers, "target": target}
