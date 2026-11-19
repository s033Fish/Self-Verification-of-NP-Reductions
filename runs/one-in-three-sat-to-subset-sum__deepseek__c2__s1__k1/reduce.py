"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

The source problem is positive 1-in-3-SAT: variables 1..m, clauses are
triples of distinct positive variables, and a clause is satisfied exactly
when exactly one of its three variables is true.

Reduction
---------
Let the clauses be C_0, ..., C_{k-1}.  Use base B = 4 (strictly larger
than the maximum number of true occurrences in a clause, which is 3).
For every variable x that occurs in at least one clause, create one
Subset-Sum item

    a_x = sum_{j : x occurs in C_j} B^j .

The target is

    t = sum_{j=0}^{k-1} B^j .

A sub-list of the a_x sums to t exactly when, for every clause index j,
the number of selected occurrences of variables in C_j is exactly 1.
Because B > 3 there are no carries between digit positions, so equality
of the total sums is equivalent to equality in every column.  Selecting
a_x means setting variable x true; variables that occur in no clause do
not affect any constraint and can be assigned arbitrarily.  Therefore the
constructed Subset-Sum instance is a yes-instance iff the original
1-in-3-SAT instance is a yes-instance.

The reduction uses O(k) big-integer operations and produces O(k) numbers,
each of O(k) bits, so it runs in polynomial time in the input size.
"""


def reduce(instance):
    clauses = instance["clauses"]
    k = len(clauses)

    # Base strictly larger than the maximum column sum (3).
    B = 4

    # powers[j] = B**j
    powers = [1] * k
    for j in range(1, k):
        powers[j] = powers[j - 1] * B

    # One item per variable that actually appears in some clause.
    # Variables that never appear are irrelevant.
    var_numbers = {}
    for j, clause in enumerate(clauses):
        p = powers[j]
        for v in clause:
            var_numbers[v] = var_numbers.get(v, 0) + p

    numbers = [var_numbers[v] for v in sorted(var_numbers)]
    target = sum(powers)

    return {"numbers": numbers, "target": target}
