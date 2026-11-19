"""Polynomial-time reduction from 1-in-3-SAT (positive) to Subset Sum.

Encoding
--------
Fix a base B larger than any possible per-digit sum.  Since a clause has
exactly 3 variables and a variable contributes to at most one digit per
clause, every digit of any subset sum is at most 3, so B = 4 is safe.

There is one digit position for each variable 1..m and one for each clause
0..k-1.

For every variable i we create two numbers:

    true_i  = B**(i-1) + sum(B**(m+j) for clauses j containing i)
    false_i = B**(i-1)

The target is

    target = sum(B**(i-1) for i in 1..m) + sum(B**(m+j) for j in 0..k-1)

Choosing exactly one of {true_i, false_i} sets variable digit i to 1, so
the variable digits force exactly one choice per variable (both -> 2,
neither -> 0, and no carries occur because every digit is < B).  A clause
digit then equals the number of true variables in that clause, and the
target's 1 forces exactly one of the three to be true.

A formula with no clauses and m = 0 yields numbers = [] and target = 0,
which Subset Sum accepts (empty sub-list).
"""


def reduce(instance):
    """Map a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    base = 4  # > 3, the maximum possible value of any digit

    # weight of variable digit i (1-indexed) and clause digit j (0-indexed)
    def var_weight(i):
        return base ** (i - 1)

    def clause_weight(j):
        return base ** (num_vars + j)

    numbers = []
    for i in range(1, num_vars + 1):
        true_value = var_weight(i)
        for j, clause in enumerate(clauses):
            if i in clause:
                true_value += clause_weight(j)
        numbers.append(true_value)
        numbers.append(var_weight(i))

    target = sum(var_weight(i) for i in range(1, num_vars + 1))
    target += sum(clause_weight(j) for j in range(len(clauses)))

    return {"numbers": numbers, "target": target}
