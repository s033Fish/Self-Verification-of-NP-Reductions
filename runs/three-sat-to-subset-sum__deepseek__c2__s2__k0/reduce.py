"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction
------------
Let the formula have m variables and n clauses.  Use base-10 digits where
digit position ``i-1`` (0-indexed) belongs to variable i (1..m) and digit
position ``m+j-1`` belongs to clause j (1..n).

Numbers
  * For every variable i, two "literal" numbers:
      T_i : digit i = 1, plus a 1 in the digit of every clause containing +i.
      F_i : digit i = 1, plus a 1 in the digit of every clause containing -i.
  * For every clause j, two identical "slack" numbers, each with a 1 in the
    digit of clause j.

Target
  * digit i = 1 for every variable i,
  * digit j = 3 for every clause j.

Why it works
  * The variable digits force a valid subset to pick exactly one of T_i / F_i
    for each variable (picking both gives 2, neither gives 0), which encodes a
    truth assignment.
  * For clause j the literal numbers contribute exactly the number k of true
    literals in that clause (k in {0,1,2,3}); the two slacks can add 0, 1 or 2.
    So the clause digit can reach 3 iff k >= 1, i.e. iff the clause is
    satisfied.
  * Every digit position receives at most 3 + 2 = 5, so there are no carries
    and base-10 representation is unique: the subset sums to the target exactly
    when the encoded assignment satisfies every clause.

The construction uses O(m + n) numbers, each with O(m + n) digits, and runs in
polynomial time.  It never calls a brute-force solver.
"""


def reduce(instance):
    """Map a 3-SAT instance to a Subset Sum instance (yes-preserving)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # pow10[k] == 10 ** k, enough positions for all variables and clauses.
    total_positions = num_vars + num_clauses
    pow10 = [1] * (total_positions + 1)
    for k in range(1, total_positions + 1):
        pow10[k] = pow10[k - 1] * 10

    numbers = []

    # One number for each literal of each variable.
    for var in range(1, num_vars + 1):
        true_number = pow10[var - 1]
        false_number = pow10[var - 1]
        for index, clause in enumerate(clauses):
            clause_digit = pow10[num_vars + index]
            if var in clause:
                true_number += clause_digit
            if -var in clause:
                false_number += clause_digit
        numbers.append(true_number)
        numbers.append(false_number)

    # Two slack numbers for each clause (each contributes 1 to its digit).
    for index in range(num_clauses):
        slack = pow10[num_vars + index]
        numbers.append(slack)
        numbers.append(slack)

    # Target: 1 per variable digit, 3 per clause digit.
    target = 0
    for var in range(1, num_vars + 1):
        target += pow10[var - 1]
    for index in range(num_clauses):
        target += 3 * pow10[num_vars + index]

    return {"numbers": numbers, "target": target}
