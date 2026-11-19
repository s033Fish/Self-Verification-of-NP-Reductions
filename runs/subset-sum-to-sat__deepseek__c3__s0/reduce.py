"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Introduce one boolean variable x_i for every non-zero number a_i, meaning
"a_i is part of the chosen sub-list".  The chosen sum is

        sum_i a_i * x_i .

We build a ripple-carry binary adder circuit that computes this sum bit by
bit and then force the resulting bits to equal the binary digits of the
target.  Every gate is encoded with the standard 3-CNF Tseitin clauses, so
the whole formula is satisfiable exactly when some sub-list sums to the
target.

The circuit has O(n * W) gates where n is the number of numbers and W is
the bit length of their total sum, hence the reduction is polynomial in the
input size (the input size itself contains all those bits).

Edge cases
----------
* target < 0            -> unsatisfiable formula (empty clause).
* target > sum(numbers) -> unsatisfiable formula (empty clause).
* target == 0           -> satisfiable formula (empty formula); the empty
                           sub-list always works.
"""


class _Builder:
    """Small helper that emits a CNF formula over fresh variables 1..m."""

    def __init__(self):
        self.num_vars = 0
        self.clauses = []

    def new_var(self):
        self.num_vars += 1
        return self.num_vars

    def add_clause(self, literals):
        self.clauses.append(list(literals))

    def const(self, value):
        """Return a literal whose truth value is fixed to `value`."""
        var = self.new_var()
        self.add_clause([var] if value else [-var])
        return var

    def and_(self, a, b):
        """Return a literal z with z <=> (a and b)."""
        z = self.new_var()
        self.add_clause([-a, -b, z])
        self.add_clause([a, -z])
        self.add_clause([b, -z])
        return z

    def or_(self, a, b):
        """Return a literal z with z <=> (a or b)."""
        z = self.new_var()
        self.add_clause([a, b, -z])
        self.add_clause([-a, z])
        self.add_clause([-b, z])
        return z

    def xor(self, a, b):
        """Return a literal z with z <=> (a xor b)."""
        z = self.new_var()
        self.add_clause([-a, -b, -z])
        self.add_clause([a, b, -z])
        self.add_clause([a, -b, z])
        self.add_clause([-a, b, z])
        return z

    def full_adder(self, a, b, carry_in):
        """Return (sum, carry_out) for one bit of a binary adder."""
        a_xor_b = self.xor(a, b)
        total = self.xor(a_xor_b, carry_in)
        carry_out = self.or_(self.and_(a, b), self.and_(carry_in, a_xor_b))
        return total, carry_out


def reduce(instance):
    """Reduce a Subset Sum instance to a SAT instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]

    # t < 0 is always "no".
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    total = sum(numbers)

    # t above the sum of all numbers is always "no".
    if target > total:
        return {"num_vars": 0, "clauses": [[]]}

    # t == 0 is always "yes" (the empty sub-list).
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    builder = _Builder()
    width = max(1, total.bit_length())

    # One boolean variable per non-zero number (zero numbers never matter).
    choice = []
    for value in numbers:
        choice.append(builder.new_var() if value != 0 else None)

    false = builder.const(False)

    # partial[k] is the k-th bit of the sum of the numbers processed so far.
    partial = [false] * width
    for value, include in zip(numbers, choice):
        if include is None:
            continue
        carry = false
        next_partial = []
        for k in range(width):
            addend = include if (value >> k) & 1 else false
            bit, carry = builder.full_adder(partial[k], addend, carry)
            next_partial.append(bit)
        partial = next_partial

    # Force the computed sum to equal the target, bit by bit.
    for k in range(width):
        if (target >> k) & 1:
            builder.add_clause([partial[k]])
        else:
            builder.add_clause([-partial[k]])

    return {"num_vars": builder.num_vars, "clauses": builder.clauses}
