"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Construction
------------
Let m = num_vars and n = len(clauses).  Work in base B = 10, with one digit
position for each variable (positions 0..m-1) and one digit position for each
clause (positions m..m+n-1).

For every variable i (1-based) create two numbers:

    T_i = B^(i-1) + sum over clauses j containing i of B^(m+j)
    F_i = B^(i-1)

Both carry a 1 in the variable-i position, so a sub-list that sums to the
target must pick exactly one of T_i, F_i for every variable (the target has a
1 there, and every column sum is at most 3 < B, hence there are no carries).
T_i contributes a 1 to each clause position in which variable i occurs, while
F_i contributes nothing there.  Therefore the digit of clause j in the sum is
exactly the number of true variables in clause j.  The target has a 1 in every
clause position, so a valid sub-list exists iff there is a truth assignment
with exactly one true variable per clause.

The construction uses O(m + n) numbers, each with O(m + n) digits, so it runs
in polynomial time in the size of the input.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10

    # Weight of the digit position for variable i (0-based) and clause j.
    def var_weight(i):
        return base ** i

    def clause_weight(j):
        return base ** (num_vars + j)

    numbers = []
    for i in range(num_vars):
        true_number = var_weight(i)
        false_number = var_weight(i)
        for j, clause in enumerate(clauses):
            if (i + 1) in clause:
                true_number += clause_weight(j)
        numbers.append(true_number)
        numbers.append(false_number)

    target = 0
    for i in range(num_vars):
        target += var_weight(i)
    for j in range(num_clauses):
        target += clause_weight(j)

    return {"numbers": numbers, "target": target}
