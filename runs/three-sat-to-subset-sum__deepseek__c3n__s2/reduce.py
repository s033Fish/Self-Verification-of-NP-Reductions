"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard digit / "base 10" reduction):

Let the formula have m variables and k clauses.  We build numbers with
m + k decimal digits.  Digit positions 0..m-1 correspond to the variables,
positions m..m+k-1 correspond to the clauses.

For each variable i (1..m) we add two numbers:
    y_i : 1 in variable position i-1, and 1 in the clause position of every
          clause that contains the literal +i.
    z_i : 1 in variable position i-1, and 1 in the clause position of every
          clause that contains the literal -i.

For each clause j we add two identical "slack" numbers:
    s_j, s_j' : 1 in clause position m+j, 0 elsewhere.

The target has digit 1 in every variable position and digit 3 in every
clause position.

A subset summing to the target must pick exactly one of {y_i, z_i} for each
variable (variable digit must be exactly 1), which corresponds to an
assignment.  A clause digit receives one contribution for each true literal
of that clause (0..3) plus 0..2 from the two slack numbers.  It can reach 3
iff at least one literal of the clause is true.  No carries occur because
every digit sum is at most 3 < 10.  Hence a satisfying assignment exists
iff the target is achievable.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    total_digits = num_vars + num_clauses

    def place(position: int) -> int:
        # Decimal weight of digit position `position` (0 = most significant).
        return 10 ** (total_digits - 1 - position)

    numbers = []

    # One pair of numbers per variable.
    for var in range(1, num_vars + 1):
        var_pos = var - 1
        true_num = place(var_pos)
        false_num = place(var_pos)
        for j, clause in enumerate(clauses):
            clause_pos = num_vars + j
            if var in clause:
                true_num += place(clause_pos)
            if -var in clause:
                false_num += place(clause_pos)
        numbers.append(true_num)
        numbers.append(false_num)

    # Two slack numbers per clause.
    for j in range(num_clauses):
        clause_pos = num_vars + j
        numbers.append(place(clause_pos))
        numbers.append(place(clause_pos))

    target = 0
    for var_pos in range(num_vars):
        target += place(var_pos)
    for j in range(num_clauses):
        target += 3 * place(num_vars + j)

    return {"numbers": numbers, "target": target}
