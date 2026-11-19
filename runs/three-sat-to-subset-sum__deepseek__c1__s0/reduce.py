"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (standard digit / base-B encoding):

Let m = num_vars and k = number of clauses.  Use m + k decimal digit
positions: position v (0-based v-1) for variable v, and position m+j for
clause j.

Numbers:
  * For every variable v, two numbers X_v and Y_v.  Both have digit 1 in
    variable-position v.  X_v additionally has digit 1 in every clause
    position whose clause contains the literal +v; Y_v likewise for -v.
  * For every clause j, two slack numbers with digit 1 and digit 2 in
    clause-position m+j (and 0 elsewhere).

Target: digit 1 in every variable position and digit 4 in every clause
position.

Why it works (base 10, so no carries):
  * A variable position receives 1 from X_v and 1 from Y_v, and the target
    digit is 1, so exactly one of X_v, Y_v is selected: a truth assignment.
  * A clause position receives one 1 from each selected literal that
    satisfies the clause (0..3), plus 0..3 from the two slack numbers
    (their digits are 1 and 2).  The target digit is 4.  If the clause is
    satisfied the contribution is 1..3 and the slacks can supply exactly
    4 - c (in {1,2,3}, always achievable with {1,2}).  If the clause is
    unsatisfied the contribution is 0 and the slacks can supply at most 3,
    so 4 is unreachable.
  * Every digit is at most 6 < 10, so there are no carries and the digit
    conditions are independent.

Edge cases: with no clauses the construction yields numbers = [] and
target = 0, which is yes (empty sub-list), matching an empty 3-SAT formula
being satisfiable.  A negative target never occurs here.
"""


def _to_int(digits, base=10):
    """Little-endian digit list -> integer."""
    value = 0
    for digit in reversed(digits):
        value = value * base + digit
    return value


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)
    num_digits = num_vars + num_clauses

    numbers = []

    # One number per literal occurrence of each variable.
    for var in range(1, num_vars + 1):
        for sign in (1, -1):
            digits = [0] * num_digits
            digits[var - 1] = 1
            for index, clause in enumerate(clauses):
                if sign * var in clause:
                    digits[num_vars + index] = 1
            numbers.append(_to_int(digits))

    # Two slack numbers per clause: digits 1 and 2.
    for index in range(num_clauses):
        digits_one = [0] * num_digits
        digits_one[num_vars + index] = 1
        numbers.append(_to_int(digits_one))

        digits_two = [0] * num_digits
        digits_two[num_vars + index] = 2
        numbers.append(_to_int(digits_two))

    # Target: 1 per variable digit, 4 per clause digit.
    target_digits = [0] * num_digits
    for var in range(num_vars):
        target_digits[var] = 1
    for index in range(num_clauses):
        target_digits[num_vars + index] = 4

    return {"numbers": numbers, "target": _to_int(target_digits)}
