"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Idea (standard digit / base-B encoding)
---------------------------------------
Let m = num_vars and k = len(clauses).  Choose a base B larger than any
possible column sum (B = k + 5 works; a clause column receives at most 3
contributions and a variable column at most 2, all < B).

Use one digit position per variable (positions 0..m-1) and one digit
position per clause (positions m..m+k-1).

For every variable i create two numbers:
    true_i  = B^(i-1) + sum over clauses j containing i of B^(m+j)
    false_i = B^(i-1)

Target:
    T = sum_{i=1..m} B^(i-1) + sum_{j=0..k-1} B^(m+j)

Every variable digit of T is 1, and only true_i / false_i touch it, so
exactly one of the pair must be picked (giving digit 1).  Every clause
digit of T is 1, and its only contributions come from the true_i of the
variables occurring in that clause, so the clause contributes exactly the
number of its variables that are set true.  Hence the digit is 1 exactly
when the clause has exactly one true variable.  Because every column sum
is < B there are no carries, so the digit equations hold exactly.

Therefore a subset sums to T iff the chosen literals describe an
assignment making exactly one variable true in every clause.

The construction uses 2m numbers whose bit lengths are polynomial in the
instance size, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # Base big enough that no column ever carries (max column sum is 3).
    base = k + 5

    def weight(position):
        return base ** position

    # Position of variable i (1-based) is i-1; position of clause j is m+j.
    numbers = []

    for i in range(1, num_vars + 1):
        var_digit = weight(i - 1)
        true_number = var_digit
        for j, clause in enumerate(clauses):
            if i in clause:
                true_number += weight(num_vars + j)
        numbers.append(true_number)
        numbers.append(var_digit)  # false: variable digit only

    target = sum(weight(i - 1) for i in range(1, num_vars + 1))
    target += sum(weight(num_vars + j) for j in range(k))

    return {"numbers": numbers, "target": target}
