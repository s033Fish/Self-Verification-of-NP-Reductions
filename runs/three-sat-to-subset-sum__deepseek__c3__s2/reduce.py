"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (the standard "digit column" reduction)
----------------------------------------------------
Let the formula have m variables and n clauses.  Choose a base B larger than
the maximum possible digit sum in any column (5), e.g. B = 10.  We use
m + n digit positions:

  * positions 0 .. m-1      : one "variable" column per variable,
  * positions m .. m+n-1    : one "clause" column per clause.

For every variable i (1-indexed) create two numbers:

  * T_i = B^(i-1) + sum over clauses j containing literal +i of B^(m+j)
  * F_i = B^(i-1) + sum over clauses j containing literal -i of B^(m+j)

For every clause j create two identical "slack" numbers S_j = B^(m+j).

The target is

  target = sum_{i=0}^{m-1} B^i + sum_{j=0}^{n-1} 3 * B^(m+j),

i.e. digit 1 in every variable column and digit 3 in every clause column.

Correctness
-----------
No column can ever carry: a variable column receives at most one of T_i/F_i
(digit <= 1... actually <= 2 but still < B), and a clause column receives at
most 3 from variable numbers (a clause has 3 literals on distinct variables)
plus 2 from the two slacks, i.e. at most 5 < B.  Hence a subset sums to the
target iff it matches digit by digit.

  * (SAT -> subset)  Pick T_i for true variables and F_i for false ones.
    Every variable column then reads 1.  A satisfied clause has at least one
    true literal, so its column already reads 1..3 from the chosen variable
    numbers; add 3 - (that value) of the two slack numbers (0, 1 or 2 of
    them) to make the column read exactly 3.
  * (subset -> SAT)  The variable column i must read exactly 1, so exactly
    one of T_i/F_i is chosen: read off a consistent assignment.  A clause
    column must read 3, but the two slacks contribute at most 2, so the
    variable numbers must contribute at least 1, i.e. some literal of the
    clause is true.  The assignment satisfies every clause.

Edge cases: no clauses -> target is just the variable part and choosing one
of each pair works (yes); m = 0 and n = 0 -> empty number list and target 0
(yes).
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)
    base = 10

    # target: 1 in every variable column, 3 in every clause column
    target = 0
    for i in range(num_vars):
        target += base ** i
    for j in range(n):
        target += 3 * base ** (num_vars + j)

    numbers = []
    for i in range(1, num_vars + 1):
        true_number = base ** (i - 1)
        false_number = base ** (i - 1)
        for j, clause in enumerate(clauses):
            if i in clause:
                true_number += base ** (num_vars + j)
            if -i in clause:
                false_number += base ** (num_vars + j)
        numbers.append(true_number)
        numbers.append(false_number)

    # two slack numbers per clause
    for j in range(n):
        numbers.append(base ** (num_vars + j))
        numbers.append(base ** (num_vars + j))

    return {"numbers": numbers, "target": target}
