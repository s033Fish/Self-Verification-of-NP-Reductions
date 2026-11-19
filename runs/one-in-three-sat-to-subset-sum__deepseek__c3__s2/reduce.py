"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Construction (base-10 digit encoding)
-------------------------------------
There are ``m + n`` digit positions, where ``m = num_vars`` and
``n = len(clauses)``:

* positions ``0 .. m-1``  correspond to the variables 1..m,
* positions ``m .. m+n-1`` correspond to the clauses.

For every variable ``i`` (1-based) we emit two numbers:

* ``A_i`` ("x_i is true"): digit 1 in variable position ``i-1`` and digit 1
  in the position of every clause that contains ``i``.
* ``B_i`` ("x_i is false"): digit 1 in variable position ``i-1`` and digit 0
  everywhere else.

The target has digit 1 in every variable position and digit 1 in every
clause position.

Why it works
------------
Every digit sum is at most 3 (a clause has three variables) and the base is
10, so there are never any carries: each position is independent.

* Variable position ``i-1``: only ``A_i`` and ``B_i`` have a 1 there.  The
  target asks for exactly 1, so a valid subset selects exactly one of them.
  This is a total assignment of truth values to all variables.
* Clause position ``j``: the digit of the chosen subset equals the number of
  selected ``A_i`` among the three variables of clause ``j``, i.e. the number
  of true variables in that clause.  The target asks for exactly 1, so every
  clause has exactly one true variable.

Hence the subset-sum instance is yes iff the formula is 1-in-3 satisfiable.
The instance has ``2m`` numbers, each with ``m + n`` decimal digits, so the
reduction is polynomial time and produces a polynomial-size instance.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    base = 10
    num_positions = num_vars + num_clauses

    def encode(digits):
        value = 0
        for digit in digits:
            value = value * base + digit
        return value

    # Precompute, for each variable, the clauses containing it.
    clause_positions = {i: [] for i in range(1, num_vars + 1)}
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_positions[var].append(num_vars + j)

    numbers = []
    for i in range(1, num_vars + 1):
        # A_i: true -> contributes 1 to each clause containing i.
        digits = [0] * num_positions
        digits[i - 1] = 1
        for pos in clause_positions[i]:
            digits[pos] = 1
        numbers.append(encode(digits))

        # B_i: false -> contributes only to the variable position.
        digits = [0] * num_positions
        digits[i - 1] = 1
        numbers.append(encode(digits))

    target_digits = [0] * num_positions
    for i in range(num_vars):
        target_digits[i] = 1
    for j in range(num_clauses):
        target_digits[num_vars + j] = 1
    target = encode(target_digits)

    return {"numbers": numbers, "target": target}
