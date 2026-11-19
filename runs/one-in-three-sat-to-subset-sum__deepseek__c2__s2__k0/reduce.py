"""Polynomial-time reduction from positive 1-in-3-SAT to Subset Sum.

Encoding
--------
Use base B = 4.  There is one digit position for every variable and one
digit position for every clause occurrence.

For each variable i (1..m) create two numbers:

    T_i = B^(i-1) + sum over clauses j containing i of B^(m+j)
    F_i = B^(i-1)

The target has digit 1 in every variable position and digit 1 in every
clause position.

Selecting exactly one of T_i, F_i makes variable position i sum to 1, so
each variable receives a truth value (T_i selected means true).  A clause
position j receives one unit from each true variable occurring in clause j,
so it sums to 1 exactly when that clause has exactly one true variable.

At most 3 units can enter a clause position (a clause has 3 variables) and
at most 2 units can enter a variable position, so no carries occur in base
4.  Therefore the subset sum equals the target iff the selected numbers
describe a satisfying assignment, giving a bijection between satisfying
assignments and solutions of the constructed Subset Sum instance.

The construction uses O(m + c) digit positions and O(m) numbers, each of
size polynomial in m + c, so it runs in polynomial time.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 1-in-3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)
    base = 4

    # powers[k] = base**k, one entry per digit position.
    powers = [1] * (m + c)
    for k in range(1, m + c):
        powers[k] = powers[k - 1] * base

    # Target: digit 1 in each variable position and each clause position.
    target = 0
    for i in range(m):
        target += powers[i]
    for j in range(c):
        target += powers[m + j]

    # Clause occurrences containing each variable.
    occurrences = [[] for _ in range(m + 1)]
    for j, clause in enumerate(clauses):
        for v in clause:
            occurrences[v].append(j)

    numbers = []
    for i in range(1, m + 1):
        var_digit = powers[i - 1]
        true_number = var_digit
        for j in occurrences[i]:
            true_number += powers[m + j]
        numbers.append(true_number)  # variable i is true
        numbers.append(var_digit)    # variable i is false

    return {"numbers": numbers, "target": target}
