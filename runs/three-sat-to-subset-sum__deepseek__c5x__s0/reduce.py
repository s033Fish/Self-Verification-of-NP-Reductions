"""Polynomial-time reduction from 3-SAT (ThreeSat) to Subset Sum (SubsetSum).

Standard digit-encoding reduction.

Let the source instance have m variables and n clauses.

We build numbers in base 10 with m + n digit positions:

  * positions 0 .. m-1   : one position per variable
  * positions m .. m+n-1 : one position per clause

For every variable v (1..m) we create two numbers:

  T_v = 10^(v-1) + sum over clauses j containing literal +v of 10^(m+j)
  F_v = 10^(v-1) + sum over clauses j containing literal -v of 10^(m+j)

So selecting T_v means "v is true", selecting F_v means "v is false".
Each contributes 1 to the variable-v digit, and 1 to the clause digit of
every clause it satisfies.

For every clause j we add two slack numbers 10^(m+j) and 2*10^(m+j),
which can complete a clause digit of 0,1,2,3 up to 3.

The target has digit 1 in every variable position and digit 3 in every
clause position.

A subset summing to the target must pick exactly one of {T_v, F_v} per
variable (giving digit 1 in each variable position), i.e. a truth
assignment.  In clause position j the chosen literals contribute the
number of satisfied literals (0..3); the slack numbers can make the digit
exactly 3 iff at least one literal is satisfied.  Hence a subset summing
to the target exists iff the formula is satisfiable.

No digit ever exceeds 3 (literals) + 3 (slack) = 6 < 10, so there are no
carries.  The construction uses O(m+n) numbers with O(m+n) digits, so it
runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a ThreeSat instance to an equivalent SubsetSum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # weight of the digit position for variable v (1-based)
    def var_digit(v):
        return 10 ** (v - 1)

    # weight of the digit position for clause j (0-based)
    def clause_digit(j):
        return 10 ** (num_vars + j)

    numbers = []

    for v in range(1, num_vars + 1):
        true_num = var_digit(v)
        false_num = var_digit(v)
        for j, clause in enumerate(clauses):
            if v in clause:
                true_num += clause_digit(j)
            if -v in clause:
                false_num += clause_digit(j)
        numbers.append(true_num)
        numbers.append(false_num)

    for j in range(num_clauses):
        numbers.append(clause_digit(j))
        numbers.append(2 * clause_digit(j))

    target = sum(var_digit(v) for v in range(1, num_vars + 1))
    target += sum(3 * clause_digit(j) for j in range(num_clauses))

    return {"numbers": numbers, "target": target}
