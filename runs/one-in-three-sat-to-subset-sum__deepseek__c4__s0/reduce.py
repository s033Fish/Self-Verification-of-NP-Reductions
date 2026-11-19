"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Encoding
--------
Fix a base B (we use B = 4).  We use one digit position per variable
(positions 0 .. m-1) and one digit position per clause (positions m .. m+k-1),
where m = num_vars and k = number of clauses.

For each variable i (1..m) we create two numbers:

    T_i : digit 1 at variable position i-1, and digit 1 at every clause
          position of a clause that contains variable i.
    F_i : digit 1 at variable position i-1 only.

The target has digit 1 at *every* position.

Because only T_i and F_i have a non-zero digit at variable position i-1,
and the target digit there is 1, any solution must pick exactly one of
T_i / F_i.  Picking T_i means "variable i is true".  Then the digit at a
clause position equals the number of true variables in that clause, and the
target digit there is 1, so every clause has exactly one true variable.

The maximum raw digit sum is 3 (a clause has 3 distinct variables), and
B = 4 > 3, so no carries ever occur: a subset sums to the target iff its
digit sums match the target digit-wise.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    base = 4  # > maximum raw digit sum (3), so there are no carries
    num_clause_positions = len(clauses)

    def value(digits):
        total = 0
        for pos, digit in digits.items():
            total += digit * (base ** pos)
        return total

    numbers = []
    for var in range(1, num_vars + 1):
        var_pos = var - 1
        # T_var: variable position plus the clause positions it occurs in.
        true_digits = {var_pos: 1}
        for clause_index, clause in enumerate(clauses):
            if var in clause:
                true_digits[num_vars + clause_index] = 1
        numbers.append(value(true_digits))
        # F_var: only the variable position.
        numbers.append(value({var_pos: 1}))

    # Target: digit 1 at every position.
    target = 0
    for pos in range(num_vars + num_clause_positions):
        target += base ** pos

    return {"numbers": numbers, "target": target}
