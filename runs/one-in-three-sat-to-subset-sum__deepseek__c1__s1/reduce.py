"""Polynomial-time reduction from positive 1-in-3-SAT to Subset Sum.

Reduction
---------
Only variables that actually occur in clauses matter: a variable that
occurs in no clause can be assigned arbitrarily and never affects the
answer.  Relabel those occurring variables as 1..n (n <= 3 * number of
clauses) and choose base B = 4.

For each relabelled variable i create two numbers

    t_i = B^i + sum over clauses j containing i of B^(n+1+j)
    f_i = B^i

and set the target

    T = sum_{i=1..n} B^i + sum_{j=0..k-1} B^(n+1+j).

Digit i of T is 1, and only t_i and f_i have a 1 in that digit, so any
subset summing to T must choose exactly one of t_i, f_i.  This encodes
the truth value of variable i.  Digit n+1+j of T is also 1, and it gets
a contribution from t_i exactly when variable i occurs in clause j.
Therefore that digit counts the number of true variables in clause j,
and it equals 1 exactly when the clause has exactly one true variable.

Every column sum is at most 3 < B, so no carries occur and the digit
arguments are exact.  The output has O(n + k) numbers, each with
O(n + k) base-4 digits, so the reduction runs in polynomial time.
"""


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 1-in-3-SAT instance."""
    clauses = instance["clauses"]

    # Relabel the variables that actually occur in clauses to 1..n.
    var_map = {}
    for clause in clauses:
        for var in clause:
            if var not in var_map:
                var_map[var] = len(var_map) + 1
    n = len(var_map)
    k = len(clauses)

    B = 4

    # For each variable, collect the indices of the clauses containing it.
    occurrences = [[] for _ in range(n + 1)]
    for j, clause in enumerate(clauses):
        for var in clause:
            occurrences[var_map[var]].append(j)

    numbers = []
    for i in range(1, n + 1):
        base = B ** i
        clause_part = 0
        for j in occurrences[i]:
            clause_part += B ** (n + 1 + j)
        numbers.append(base + clause_part)  # t_i
        numbers.append(base)                # f_i

    target = sum(B ** i for i in range(1, n + 1))
    target += sum(B ** (n + 1 + j) for j in range(k))

    return {"numbers": numbers, "target": target}
