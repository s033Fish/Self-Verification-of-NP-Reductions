"""Polynomial-time reduction from positive 1-in-3-SAT to Subset Sum.

For an instance with m variables and n clauses we use a positional
(base ``B``) encoding with one digit column per variable and one digit
column per clause.

For each variable i (1 <= i <= m) we create two numbers:

    T_i = B^(i-1) + sum over clauses c containing i of B^(m+c)
    F_i = B^(i-1)

Selecting T_i means variable i is true, selecting F_i means it is false.
No other number has a non-zero digit in variable column i, so the target
digit 1 in that column forces exactly one of T_i, F_i to be selected.

Only the T_i numbers contribute to clause columns: T_i contributes 1 to
the column of every clause containing i.  Hence the digit of clause c in
the subset sum is exactly the number of true variables in clause c.  The
target has digit 1 in every clause column, so a subset summing to the
target exists iff there is an assignment with exactly one true variable
per clause.

Choosing B > 3 (e.g. B = max(m, 3) + 2) prevents carries, since each
digit of any subset sum is at most 3.  The construction has 2m numbers
and O(m + n) digit columns, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a positive 1-in-3-SAT instance to a Subset Sum instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Large enough base so that no digit ever carries.
    base = max(m, 3) + 2

    # powers[k] = base ** k, for all digit positions we use.
    powers = [1] * (m + n)
    for k in range(1, m + n):
        powers[k] = powers[k - 1] * base

    # Target: digit 1 in every variable column and in every clause column.
    target = 0
    for i in range(m):
        target += powers[i]
    for c in range(n):
        target += powers[m + c]

    numbers = []
    for i in range(m):
        variable_digit = powers[i]
        true_number = variable_digit
        for c, clause in enumerate(clauses):
            if (i + 1) in clause:
                true_number += powers[m + c]
        # Selecting true_number encodes "variable i+1 is true";
        # selecting variable_digit encodes "variable i+1 is false".
        numbers.append(true_number)
        numbers.append(variable_digit)

    return {"numbers": numbers, "target": target}
