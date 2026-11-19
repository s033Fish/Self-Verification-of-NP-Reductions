"""Polynomial-time reduction from 3-SAT (SOURCE) to Subset Sum (TARGET).

Standard digit construction.  Choose a base B = 10 (larger than the maximum
digit sum, which is 5, so there are never any carries between digit
positions).  Use one digit position per variable and one per clause.

For every variable v (1..num_vars) add two numbers:
  * T_v: a 1 in variable-position v, plus a 1 in the clause-position of every
    clause that contains the literal +v.
  * F_v: a 1 in variable-position v, plus a 1 in the clause-position of every
    clause that contains the literal -v.

For every clause add two "slack" numbers, each with a single 1 in that
clause's position.

The target has a 1 in every variable position and a 3 in every clause
position.

Selecting exactly one of T_v / F_v per variable makes the variable digits
come out to 1 and encodes a truth assignment.  A clause position then
receives one 1 for each satisfied literal (0..3); the two slack numbers can
top it up to exactly 3 iff at least one literal is satisfied.  Since every
digit sum is at most 5 < 10, no carries can hide a mismatch, so the subset
sum instance is a yes-instance exactly when the formula is satisfiable.
"""

BASE = 10


def reduce(instance):
    """Return a Subset Sum instance equivalent to the given 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    def place(position):
        return BASE ** position

    numbers = []

    # One pair of numbers per variable.
    for var in range(1, num_vars + 1):
        true_num = place(var - 1)
        false_num = place(var - 1)
        for index, clause in enumerate(clauses):
            if var in clause:
                true_num += place(num_vars + index)
            if -var in clause:
                false_num += place(num_vars + index)
        numbers.append(true_num)
        numbers.append(false_num)

    # Two slack numbers per clause.
    for index in range(num_clauses):
        numbers.append(place(num_vars + index))
        numbers.append(place(num_vars + index))

    target = sum(place(var - 1) for var in range(1, num_vars + 1))
    target += 3 * sum(place(num_vars + index) for index in range(num_clauses))

    return {"numbers": numbers, "target": target}
