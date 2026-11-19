"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Source instance (1-in-3-SAT, positive):
    {"num_vars": m, "clauses": [[a, b, c], ...]}

Target instance (Subset Sum):
    {"numbers": [...], "target": t}

Construction
------------
Fix a base B = 4 (large enough that no digit position ever carries: a
clause digit is the sum of at most 3 contributions, a variable digit the
sum of at most 2).  Use m "variable" digit positions (0 .. m-1) and n
"clause" digit positions (m .. m+n-1), where n is the number of clauses.

For each variable i in 1..m create two numbers:

    T_i = B^(i-1) + sum over clauses j containing i of B^(m+j)
    F_i = B^(i-1)

The target is

    t = sum_{i=1..m} B^(i-1) + sum_{j=0..n-1} B^(m+j)

Correctness
-----------
* Only T_i and F_i have a 1 in variable position i-1, and the target has a
  1 there, so a valid sub-list must contain exactly one of T_i, F_i.  This
  encodes the truth value of variable i (T_i chosen <=> variable i true).
* Clause position j receives a 1 from T_i exactly when variable i occurs in
  clause j and is set true.  Hence the digit at position j equals the number
  of true variables in clause j.  The target requires this digit to be 1, so
  every clause has exactly one true variable.
* Because every digit sum is at most 3 < B = 4, there are no carries and the
  base-B digits of a sum are exactly the digit-wise sums.  Thus a sub-list
  sums to the target iff it selects exactly one number per variable and the
  induced assignment makes every clause have exactly one true variable.

The construction uses O(m + n) numbers, each of bit length O(m + n), so it
runs in polynomial time and never calls a solver.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 1-in-3-SAT one."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    base = 4

    # T_i accumulates clause-position contributions; F_i is just B^(i-1).
    true_numbers = [base ** i for i in range(num_vars)]
    false_numbers = [base ** i for i in range(num_vars)]

    for j, clause in enumerate(clauses):
        clause_position = base ** (num_vars + j)
        for var in clause:
            true_numbers[var - 1] += clause_position

    numbers = []
    for i in range(num_vars):
        numbers.append(true_numbers[i])
        numbers.append(false_numbers[i])

    target = 0
    for i in range(num_vars):
        target += base ** i
    for j in range(len(clauses)):
        target += base ** (num_vars + j)

    return {"numbers": numbers, "target": target}
