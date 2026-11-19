"""Polynomial-time reduction from 1-in-3-SAT (positive) to Subset Sum.

Encoding
--------
Let m = num_vars and c = len(clauses).  Work in base B = 10, using one digit
position per variable (positions 0..m-1) and one digit position per clause
occurrence (positions m..m+c-1).

For each variable i (1-indexed, 0-indexed position p = i-1) emit two numbers:

    a_i = B^p + sum over clause occurrences j containing i of B^(m+j)
    b_i = B^p

Choosing a_i encodes "x_i = true", choosing b_i encodes "x_i = false".

Target: digit 1 in every position, i.e.
    T = sum_{p=0}^{m-1} B^p + sum_{j=0}^{c-1} B^(m+j)

Why it works
------------
* Only a_i and b_i have a nonzero digit in variable position p, so the target
  digit 1 there forces exactly one of them to be chosen.  Hence a subset
  summing to T corresponds to a total assignment of the variables.
* In clause position m+j, the only contributors are the a_i for the three
  variables appearing in clause j (each contributes 1).  So that digit equals
  the number of true variables in clause j; target digit 1 forces exactly one.
* Every digit sum is at most 3 < B = 10, so there are no carries and the
  digit-wise reasoning is exact.

The construction is polynomial: O(m) numbers, each with O(m + c) digits.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    c = len(clauses)
    B = 10

    target = 0
    for p in range(m):
        target += B ** p
    for j in range(c):
        target += B ** (m + j)

    numbers = []
    for i in range(1, m + 1):
        p = i - 1
        base = B ** p
        true_num = base
        for j, clause in enumerate(clauses):
            if i in clause:
                true_num += B ** (m + j)
        numbers.append(true_num)  # a_i : x_i = true
        numbers.append(base)      # b_i : x_i = false

    return {"numbers": numbers, "target": target}
