"""Polynomial-time reduction from 3-SAT (ThreeSat) to Subset Sum (SubsetSum).

Construction (standard digit / "big number" reduction):

Pick base B = 10 (any base > 5 works, since no digit sum ever exceeds 5).

There is one digit position per variable and one per clause.  Positions are
weighted B**0 .. B**(num_vars + num_clauses - 1).

For every variable v (1..m) add two numbers:
  * T_v : 1 in variable-digit v, plus 1 in the clause-digit of every clause
          that contains the literal +v.
  * F_v : 1 in variable-digit v, plus 1 in the clause-digit of every clause
          that contains the literal -v.
For every clause j add two "slack" numbers, each with a 1 in clause-digit j.

Target: 1 in every variable digit, and 3 in every clause digit.

Why it works:
  * Variable digit v: only T_v and F_v touch it, each contributing 1, so the
    target's 1 forces exactly one of T_v / F_v to be selected -> a truth value.
  * Clause digit j: the two slacks contribute at most 2, and each of the three
    literals of clause j contributes 1 iff that literal is made true.  Target 3
    is reachable iff at least one literal contributes, i.e. the clause is
    satisfied (the slacks fill the remaining 1 or 2).
  * No carries occur because every digit sum is at most 5 < 10, so the digit
    positions are independent.
"""

BASE = 10


def reduce(instance):
    """Reduce a ThreeSat instance to a SubsetSum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # powers[d] = BASE ** d
    total_digits = num_vars + num_clauses
    powers = [1] * (total_digits + 1)
    for d in range(1, total_digits + 1):
        powers[d] = powers[d - 1] * BASE

    def clause_digit(j):
        return powers[num_vars + j]

    numbers = []

    # Literal numbers: one per variable per polarity.
    for v in range(1, num_vars + 1):
        pos = powers[v - 1]
        neg = powers[v - 1]
        for j, clause in enumerate(clauses):
            if v in clause:
                pos += clause_digit(j)
            if -v in clause:
                neg += clause_digit(j)
        numbers.append(pos)
        numbers.append(neg)

    # Two slack numbers per clause.
    for j in range(num_clauses):
        numbers.append(clause_digit(j))
        numbers.append(clause_digit(j))

    # Target: 1 per variable digit, 3 per clause digit.
    target = 0
    for v in range(1, num_vars + 1):
        target += powers[v - 1]
    for j in range(num_clauses):
        target += 3 * clause_digit(j)

    return {"numbers": numbers, "target": target}
