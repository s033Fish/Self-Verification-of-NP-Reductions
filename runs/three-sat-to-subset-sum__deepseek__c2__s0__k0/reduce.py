"""Polynomial-time reduction from 3-SAT to Subset Sum.

Encoding
--------
Fix a base B = 10.  Every number is written in base B with one digit per
variable (positions 0 .. m-1) followed by one digit per clause
(positions m .. m+n-1).  Because every digit in every produced number is at
most 1, and at most 3 literal numbers plus 2 slack numbers can hit any single
clause digit, no digit column ever exceeds 5 < B.  Hence there are no carries
and a sum equals the target iff it matches the target digit by digit.

Numbers
-------
* For each variable v there are two numbers:
    - "v is true":  digit 1 in the variable-v position, plus digit 1 in the
      clause position of every clause containing the literal +v;
    - "v is false": digit 1 in the variable-v position, plus digit 1 in the
      clause position of every clause containing the literal -v.
* For each clause there are two slack numbers, each with digit 1 only in that
  clause's position.

Target
------
* digit 1 in every variable position (forces choosing exactly one of the two
  numbers of each variable, i.e. a total assignment);
* digit 3 in every clause position (a clause must receive at least one true
  literal; the two slacks can top a contribution of 1 or 2 up to 3, but
  cannot manufacture a contribution of 0).

Thus the target is reachable iff the formula is satisfiable.  The instance has
2m + 2n numbers, each with O(m + n) digits, so the construction is polynomial
in the size of the formula.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10

    def var_exp(v):
        # Exponent of the digit for variable v (1-based).
        return v - 1

    def clause_exp(j):
        # Exponent of the digit for clause j (0-based).
        return num_vars + j

    numbers = []

    # One pair of numbers per variable.
    for v in range(1, num_vars + 1):
        true_num = base ** var_exp(v)
        false_num = base ** var_exp(v)
        for j, clause in enumerate(clauses):
            if v in clause:
                true_num += base ** clause_exp(j)
            if -v in clause:
                false_num += base ** clause_exp(j)
        numbers.append(true_num)
        numbers.append(false_num)

    # Two slack numbers per clause.
    for j in range(num_clauses):
        slack = base ** clause_exp(j)
        numbers.append(slack)
        numbers.append(slack)

    # Target: one unit per variable, three units per clause.
    target = 0
    for v in range(1, num_vars + 1):
        target += base ** var_exp(v)
    for j in range(num_clauses):
        target += 3 * base ** clause_exp(j)

    return {"numbers": numbers, "target": target}
