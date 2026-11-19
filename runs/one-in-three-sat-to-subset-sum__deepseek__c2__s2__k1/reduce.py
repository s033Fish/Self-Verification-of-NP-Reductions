"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

For a formula with m variables and k clauses, use base B = 4 (larger than
any possible digit sum, so no carries can occur).

Digit positions:
  * positions 0 .. k-1          : one position per clause
  * positions k .. k+m-1        : one position per variable

For every variable i in 1..m create two numbers:
  * T_i has digit 1 in variable position i and digit 1 in every clause
    position whose clause contains i (this number represents i = true).
  * F_i has digit 1 in variable position i and no clause digits (this
    number represents i = false).

The target has digit 1 in every variable position and digit 1 in every
clause position.

A subset sum equals the target exactly when:
  * each variable digit is 1, i.e. exactly one of T_i, F_i is chosen; and
  * each clause digit is 1, i.e. exactly one variable of that clause was
    chosen as true.

Because every digit sum is at most 3 < B, there are no carries, so the
digits can be checked independently.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    k = len(clauses)
    base = 4

    # clause_positions[i] = list of clause indices containing variable i
    clause_positions = {i: [] for i in range(1, num_vars + 1)}
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_positions[var].append(j)

    numbers = []
    for i in range(1, num_vars + 1):
        var_digit = base ** (k + i - 1)
        true_number = var_digit + sum(base ** j for j in clause_positions[i])
        false_number = var_digit
        numbers.append(true_number)
        numbers.append(false_number)

    target = sum(base ** (k + i - 1) for i in range(1, num_vars + 1))
    target += sum(base ** j for j in range(k))

    return {"numbers": numbers, "target": target}
