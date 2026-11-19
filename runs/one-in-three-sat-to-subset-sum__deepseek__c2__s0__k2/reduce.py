"""Polynomial-time reduction from positive 1-in-3-SAT to Subset Sum.

SOURCE: OneInThreeSat
    instance = {"num_vars": m, "clauses": [[a, b, c], ...]}
    Yes iff some assignment of true/false to variables 1..m makes exactly one
    variable in every clause true.

TARGET: SubsetSum
    instance = {"numbers": [...], "target": t}
    Yes iff some sub-list sums to exactly t.

Construction
------------
Fix a base B = 4, which is strictly larger than any digit sum that can occur
(variable digits receive at most 2, clause digits at most 3).  Use one digit
position per variable (positions 0 .. m-1) and one per clause (positions
m .. m+n-1).

For each variable v in 1..m create two numbers:

    T_v = B**(v-1) + sum over clauses j containing v of B**(m+j)
    F_v = B**(v-1)

The target is

    t = sum_{i=0}^{m-1} B**i  +  sum_{j=0}^{n-1} B**(m+j)

Every variable digit of the target is 1, and both T_v and F_v contribute 1
there, so any solution must pick exactly one of T_v/F_v: this is the truth
value of variable v.  Because B exceeds every digit sum, there are no
carries, so each clause digit of a solution equals the number of selected
T_v among the clause's variables, i.e. the number of true variables in that
clause.  The target requires this to be exactly 1.  Hence solutions of the
Subset Sum instance correspond exactly to satisfying assignments of the
1-in-3-SAT instance, and vice versa.

The construction uses O(m + n) numbers whose bit length is O(m + n), and is
computed in polynomial time.
"""


def reduce(instance):
    """Reduce a OneInThreeSat instance to a SubsetSum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Larger than the maximum possible digit sum (3), so no carries occur.
    base = 4

    numbers = []
    for v in range(1, num_vars + 1):
        variable_digit = base ** (v - 1)
        true_number = variable_digit
        false_number = variable_digit
        for j, clause in enumerate(clauses):
            if v in clause:
                true_number += base ** (num_vars + j)
        numbers.append(true_number)
        numbers.append(false_number)

    target = sum(base ** i for i in range(num_vars))
    target += sum(base ** (num_vars + j) for j in range(n))

    return {"numbers": numbers, "target": target}
