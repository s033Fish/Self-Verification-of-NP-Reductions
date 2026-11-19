"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction
------------
Let the formula have m variables and n clauses.  Use base 10 and reserve one
column for each variable (columns 0 .. m-1) and one column for each clause
(columns m .. m+n-1).

For every variable v:
  * T_v has digit 1 in variable column v and digit 1 in the column of every
    clause containing the literal +v.
  * F_v has digit 1 in variable column v and digit 1 in the column of every
    clause containing the literal -v.

For every clause j, add two identical slack numbers, each having digit 1 only
in clause j's column.

The target has digit 1 in every variable column and digit 3 in every clause
column.

Every column of any sub-list sum is at most 5 (at most 3 from the literal
numbers of a clause plus 2 slack numbers), so base 10 gives no carries.  The
variable columns therefore force exactly one of T_v and F_v to be chosen,
encoding a truth assignment.  A clause column reaches 3 exactly when at
least one of its literals is true and the remaining amount is filled by the
two slack numbers.  Hence a subset sums to the target iff the formula is
satisfiable.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # A clause column receives at most 3 from literal numbers and 2 from
    # slack numbers, so base 10 guarantees carry-free, independent columns.
    BASE = 10

    total_columns = num_vars + n
    powers = [1] * total_columns
    for i in range(1, total_columns):
        powers[i] = powers[i - 1] * BASE

    numbers = []

    # Variable v (1-based) owns column v-1.
    for v in range(1, num_vars + 1):
        var_col = v - 1
        true_number = powers[var_col]
        false_number = powers[var_col]

        for j, clause in enumerate(clauses):
            clause_col = num_vars + j
            if v in clause:
                true_number += powers[clause_col]
            if -v in clause:
                false_number += powers[clause_col]

        numbers.append(true_number)
        numbers.append(false_number)

    # Two slack numbers for each clause.
    for j in range(n):
        clause_col = num_vars + j
        numbers.append(powers[clause_col])
        numbers.append(powers[clause_col])

    target = 0
    for v in range(1, num_vars + 1):
        target += powers[v - 1]
    for j in range(n):
        target += 3 * powers[num_vars + j]

    return {"numbers": numbers, "target": target}
