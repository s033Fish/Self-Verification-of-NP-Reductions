"""Polynomial-time reduction from positive 1-in-3-SAT to Subset Sum.

Encoding
--------
Let the formula have m variables and n clauses.  Choose base B = 4.
Use n low-order digits (positions 0..n-1) for the clauses and m further
digits (positions n..n+m-1) for the variables.

For every variable i (1..m) create two numbers:

    T_i = B^(n+i-1) + sum over clauses j containing i of B^j
    F_i = B^(n+i-1)

The target is

    target = sum_{j=0}^{n-1} B^j  +  sum_{i=0}^{m-1} B^(n+i)

Digit position n+i-1 is nonzero (equal to 1) only in T_i and F_i, so any
subset summing to the target must contain exactly one of T_i, F_i for
every variable i.  That choice is the truth assignment (T_i chosen means
variable i is true).

Digit position j (a clause) receives a 1 from T_i exactly when variable i
occurs in clause j, and 0 from every F_i.  The target has a 1 in that
position, so exactly one variable of clause j must be true.

Because every digit sum is at most 3 < B = 4, there are no carries, and
the digit-wise conditions above are necessary and sufficient.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 1-in-3-SAT one."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)
    base = 4

    # powers[k] == base ** k, for every digit position we may use.
    max_pos = n + num_vars
    powers = [1] * (max_pos + 1)
    for k in range(1, max_pos + 1):
        powers[k] = powers[k - 1] * base

    target = 0
    for j in range(n):
        target += powers[j]
    for i in range(num_vars):
        target += powers[n + i]

    numbers = []
    for i in range(1, num_vars + 1):
        variable_digit = powers[n + i - 1]
        true_number = variable_digit
        for j, clause in enumerate(clauses):
            if i in clause:
                true_number += powers[j]
        false_number = variable_digit
        numbers.append(true_number)
        numbers.append(false_number)

    return {"numbers": numbers, "target": target}
