"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction (the standard digit / base-10 encoding):

  * There is one digit position per variable and one digit position per
    clause.  We use base 10, which is large enough that no digit ever
    carries: a clause digit receives at most 3 (one per literal in the
    clause) plus at most 2 (the two slack numbers) = 5 < 10, and a
    variable digit receives at most 2.

  * For every variable v we create two numbers:
      - "v true":  1 in v's digit, and 1 in the digit of every clause
                   that contains the literal +v.
      - "v false": 1 in v's digit, and 1 in the digit of every clause
                   that contains the literal -v.

  * For every clause we create two identical slack numbers, each with a 1
    in that clause's digit and 0 elsewhere.

  * The target has 1 in every variable digit and 3 in every clause digit.

Choosing exactly one of the two numbers of each variable corresponds to an
assignment.  The variable digits of the target force exactly one choice per
variable.  In a clause digit, the chosen variable numbers contribute the
number of true literals in that clause; the two slack numbers can add 0, 1
or 2.  Hence the clause digit can reach 3 exactly when at least one literal
of the clause is true.  Therefore a subset sums to the target iff the
formula is satisfiable.

The construction uses O(num_vars + num_clauses) numbers, each with
O(num_vars + num_clauses) decimal digits, so it runs in polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10
    # Digit positions: 0 .. num_clauses-1 are clause digits,
    # num_clauses .. num_clauses+num_vars-1 are variable digits.
    num_digits = num_clauses + num_vars
    weights = [base ** i for i in range(num_digits)]

    def value(digit_counts):
        return sum(c * w for c, w in zip(digit_counts, weights))

    numbers = []

    # One pair of numbers per variable.
    for v in range(1, num_vars + 1):
        true_digits = [0] * num_digits
        false_digits = [0] * num_digits
        true_digits[num_clauses + v - 1] = 1
        false_digits[num_clauses + v - 1] = 1
        for j, clause in enumerate(clauses):
            if v in clause:
                true_digits[j] = 1
            if -v in clause:
                false_digits[j] = 1
        numbers.append(value(true_digits))
        numbers.append(value(false_digits))

    # Two slack numbers per clause.
    for j in range(num_clauses):
        slack_digits = [0] * num_digits
        slack_digits[j] = 1
        slack = value(slack_digits)
        numbers.append(slack)
        numbers.append(slack)

    # Target: 1 per variable digit, 3 per clause digit.
    target_digits = [0] * num_digits
    for j in range(num_clauses):
        target_digits[j] = 3
    for i in range(num_vars):
        target_digits[num_clauses + i] = 1
    target = value(target_digits)

    return {"numbers": numbers, "target": target}
