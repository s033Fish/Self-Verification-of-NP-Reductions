"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (the standard "digit" reduction)
---------------------------------------------
Let the 3-SAT instance have m variables and n clauses.  Work in base
B = 10 (any base > 5 works) and use m + n digit positions:

    * positions 0 .. m-1        : one "variable" position per variable
    * positions m .. m+n-1      : one "clause" position per clause

For every variable v (1..m) emit two numbers:

    T_v : digit 1 in variable position v-1, and digit 1 in the clause
          position of every clause that contains the literal +v.
    F_v : digit 1 in variable position v-1, and digit 1 in the clause
          position of every clause that contains the literal -v.

For every clause j emit two "slack" numbers, each with digit 1 in clause
position m+j and 0 elsewhere.

The target has digit 1 in every variable position and digit 3 in every
clause position.

Why it works
------------
Because every clause has exactly three literals on three distinct
variables, each clause column receives at most 3 from the variable
numbers plus at most 2 from the two slack numbers, i.e. at most 5 < 10,
so there are no carries between digit positions.

The target's variable position is 1, so for each variable exactly one of
T_v, F_v must be selected: that choice encodes the truth value of v.

A clause column must reach 3.  The slack numbers can contribute at most
2, so the selected variable numbers must contribute at least 1, i.e. at
least one selected literal satisfies the clause.  Conversely, if a
clause is satisfied its column receives between 1 and 3 from the
variables, and 0, 1 or 2 slack numbers can be added to make exactly 3.
Thus a subset summing to the target exists iff the formula is
satisfiable.

The construction uses O(m + n) numbers, each with O(m + n) digits, so it
runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance.

    Parameters
    ----------
    instance : dict
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

    Returns
    -------
    dict
        {"numbers": [...], "target": t}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10

    # weight of the digit position for variable v (1-based) and clause j (0-based)
    def var_pos(v):
        return v - 1

    def clause_pos(j):
        return num_vars + j

    numbers = []

    # Variable numbers.
    for v in range(1, num_vars + 1):
        true_num = base ** var_pos(v)
        false_num = base ** var_pos(v)
        for j, clause in enumerate(clauses):
            if v in clause:
                true_num += base ** clause_pos(j)
            if -v in clause:
                false_num += base ** clause_pos(j)
        numbers.append(true_num)
        numbers.append(false_num)

    # Slack numbers, two per clause.
    for j in range(num_clauses):
        slack = base ** clause_pos(j)
        numbers.append(slack)
        numbers.append(slack)

    # Target: 1 in each variable position, 3 in each clause position.
    target = 0
    for v in range(1, num_vars + 1):
        target += base ** var_pos(v)
    for j in range(num_clauses):
        target += 3 * base ** clause_pos(j)

    return {"numbers": numbers, "target": target}
