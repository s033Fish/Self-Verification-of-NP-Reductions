"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Encoding (base-4 positional digits):

  * digit positions 0 .. m-1          -> one per variable
  * digit positions m .. m+n-1        -> one per clause

For every variable i (1-based) we create two numbers:

  true_i  = 4^(i-1) + sum over clauses j containing i of 4^(m+j-1)
  false_i = 4^(i-1)

The target has a 1 in every variable digit and a 1 in every clause digit.

A subset selects at most one of {true_i, false_i} because the variable
digit of the target is 1 and both numbers carry a 1 there (no carries can
occur: each variable column sums to at most 2, each clause column to at
most 3, both < 4).  Hence exactly one of the two is selected for every
variable, fixing a truth assignment.  The clause digit j then equals the
number of true variables in clause j (only true_i numbers contribute to
clause columns), and the target requires it to be exactly 1.  Therefore
the Subset Sum instance is yes iff the formula has a satisfying assignment
with exactly one true variable per clause.

The construction uses 2m numbers, each with O(m+n) base-4 digits, so it
runs in polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    base = 4
    n = len(clauses)

    numbers = []
    for i in range(1, num_vars + 1):
        var_digit = base ** (i - 1)
        true_num = var_digit
        for j, clause in enumerate(clauses):
            if i in clause:
                true_num += base ** (num_vars + j)
        numbers.append(true_num)   # variable i is true
        numbers.append(var_digit)  # variable i is false

    target = 0
    for i in range(num_vars):
        target += base ** i
    for j in range(n):
        target += base ** (num_vars + j)

    return {"numbers": numbers, "target": target}
