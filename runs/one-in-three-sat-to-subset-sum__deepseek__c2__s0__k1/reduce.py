"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Source (OneInThreeSat):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    All literals positive; a clause is satisfied iff EXACTLY ONE of its three
    variables is true.

Target (SubsetSum):
    {"numbers": [...], "target": t}
    Yes iff some sub-list sums to exactly t.

Construction
------------
Work in base B = 4 (any B >= 4 works; the largest digit sum is 3).  There is
one digit position per variable (positions 0 .. m-1) and one per clause
(positions m .. m+k-1).

For every variable i (1 <= i <= m) emit two numbers:

    y_i = B**(i-1) + sum over clauses j containing i of B**(m+j)
    z_i = B**(i-1)

The variable digit i-1 receives a contribution of 1 from y_i and 1 from z_i,
and from nothing else.  The target has digit 1 there, so a valid subset must
contain exactly one of y_i, z_i: choosing both gives 2 (too big), choosing
neither gives 0 (too small).  Think of choosing y_i as "variable i is true".

Clause j = (a, b, c) has digit m+j receiving 1 from each of y_a, y_b, y_c and
0 from every other number.  The target has digit 1 there, so exactly one of
a, b, c must be true.  Hence a subset summing to the target exists iff the
formula has an assignment with exactly one true variable per clause.

Because every digit sum is at most 3 < B, there are no carries and the base-B
representation of a sum is unique, so digit-wise reasoning is exact.
"""


def reduce(instance):
    """Return a Subset Sum instance that is yes iff `instance` is yes."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    base = 4
    numbers = []

    # y_i: variable digit i-1 plus a clause digit for every clause using i.
    for i in range(1, num_vars + 1):
        value = base ** (i - 1)
        for j, clause in enumerate(clauses):
            if i in clause:
                value += base ** (num_vars + j)
        numbers.append(value)

    # z_i: only the variable digit i-1.
    for i in range(1, num_vars + 1):
        numbers.append(base ** (i - 1))

    # Target: 1 in every variable digit and 1 in every clause digit.
    target = 0
    for i in range(num_vars):
        target += base ** i
    for j in range(len(clauses)):
        target += base ** (num_vars + j)

    return {"numbers": numbers, "target": target}
