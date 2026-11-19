"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard digit / base-10 encoding)
------------------------------------------------
Let the formula have m variables and k clauses.  Use m + k decimal
"columns": column i (1 <= i <= m) is the variable column of variable i and
column m + j (1 <= j <= k) is the clause column of clause j.

Numbers (all non-negative integers, base 10, so no carries can occur):

  * For every variable i, two numbers:
        T_i = 10^i + sum over clauses j containing literal +i of 10^(m+j)
        F_i = 10^i + sum over clauses j containing literal -i of 10^(m+j)
    Thus T_i/F_i each contribute 1 to variable column i, and 1 to the
    clause columns of the clauses they satisfy.

  * For every clause j, two identical numbers 10^(m+j).  They can top a
    clause column up by at most 2.

Target:
        t = sum_{i=1..m} 10^i  +  3 * sum_{j=1..k} 10^(m+j)

Why it works
------------
No column ever exceeds 5 (variable columns get at most 1, clause columns
get at most 3 from the literals plus 2 from the clause numbers), so there
are no carries and each column must match exactly.

Variable column i must equal 1, so exactly one of T_i, F_i is chosen:
that is the truth value of variable i.  Clause column j then contains the
number s of true literals of clause j (0..3) plus c, where c in {0,1,2}
is the number of clause-j filler numbers chosen.  The column must equal 3,
which is possible iff s >= 1, i.e. iff the clause is satisfied.  Hence a
subset summing to the target exists exactly when the formula is
satisfiable.

Edge cases: with no clauses the target is sum_i 10^i and picking one of
T_i/F_i per variable hits it (yes); with m = 0 and no clauses the target
is 0 and the empty sub-list works (yes).
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10
    numbers = []

    # Variable numbers: one true-number and one false-number per variable.
    for var in range(1, num_vars + 1):
        true_num = base ** var
        false_num = base ** var
        for j, clause in enumerate(clauses):
            column = base ** (num_vars + 1 + j)
            if var in clause:
                true_num += column
            if -var in clause:
                false_num += column
        numbers.append(true_num)
        numbers.append(false_num)

    # Two filler numbers per clause, each contributing 1 to that clause column.
    for j in range(num_clauses):
        filler = base ** (num_vars + 1 + j)
        numbers.append(filler)
        numbers.append(filler)

    # Target: 1 in every variable column, 3 in every clause column.
    target = 0
    for var in range(1, num_vars + 1):
        target += base ** var
    for j in range(num_clauses):
        target += 3 * base ** (num_vars + 1 + j)

    return {"numbers": numbers, "target": target}
