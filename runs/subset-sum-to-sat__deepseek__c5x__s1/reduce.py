"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
For numbers a_1..a_n introduce a boolean variable x_i meaning "a_i is chosen".
The chosen sum is sum_i a_i * x_i.  We build a binary ripple-carry adder
circuit that computes this sum bit by bit (each a_i * x_i is just x_i placed
at the set bit positions of a_i), then add unit clauses forcing every bit of
the computed sum to equal the corresponding bit of the target t.

The circuit is Tseitin-encoded: every gate gets a fresh variable and a small
set of clauses defining it.  The number of bits needed is
W = bit_length(max(sum(numbers), t)) + O(1), which is polynomial in the input
size, so the whole construction is polynomial.

Edge cases
----------
* t < 0        -> unsatisfiable formula.
* t = 0        -> satisfiable formula (empty subset).
* t > sum(nums)-> unsatisfiable formula.
"""

from __future__ import annotations

from typing import Any


class _Encoder:
    """Builds a CNF formula over variables 1..num_vars."""

    def __init__(self) -> None:
        self.num_vars = 0
        self.clauses: list[list[int]] = []

    def new_var(self) -> int:
        self.num_vars += 1
        return self.num_vars

    def add_clause(self, clause: list[int]) -> None:
        self.clauses.append(list(clause))

    def const(self, value: bool) -> int:
        """A variable pinned to a constant truth value."""
        v = self.new_var()
        self.add_clause([v] if value else [-v])
        return v

    # ---- gates: each returns a literal equal to the gate's output ----

    def xor(self, a: int, b: int) -> int:
        z = self.new_var()
        self.add_clause([-a, -b, -z])
        self.add_clause([a, b, -z])
        self.add_clause([a, -b, z])
        self.add_clause([-a, b, z])
        return z

    def and_(self, a: int, b: int) -> int:
        z = self.new_var()
        self.add_clause([-a, -b, z])
        self.add_clause([a, -z])
        self.add_clause([b, -z])
        return z

    def or_(self, a: int, b: int) -> int:
        z = self.new_var()
        self.add_clause([a, b, -z])
        self.add_clause([-a, z])
        self.add_clause([-b, z])
        return z

    def full_adder(self, a: int, b: int, cin: int) -> tuple[int, int]:
        """Return (sum, carry_out) for a + b + cin (all single bits)."""
        t = self.xor(a, b)
        s = self.xor(t, cin)
        u = self.and_(a, b)
        v = self.and_(a, cin)
        w = self.and_(b, cin)
        p = self.or_(u, v)
        cout = self.or_(p, w)
        return s, cout


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = instance["numbers"]
    target = instance["target"]

    # --- trivial edge cases -------------------------------------------------
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}   # unsatisfiable
    if target == 0:
        return {"num_vars": 0, "clauses": []}     # satisfiable (empty subset)

    total = sum(numbers)
    if total < target:
        return {"num_vars": 0, "clauses": [[]]}   # unsatisfiable

    enc = _Encoder()
    false = enc.const(False)

    # Enough bits to hold every partial sum (all <= total) and the target.
    width = max(total.bit_length(), target.bit_length(), 1)

    acc = [false] * width  # accumulator, initially 0

    for a in numbers:
        x = enc.new_var()  # x is true iff this number is selected
        carry = false
        for j in range(width):
            bit = x if (a >> j) & 1 else false
            s, carry = enc.full_adder(acc[j], bit, carry)
            acc[j] = s
        # carry out of the top bit is 0 because the true sum < 2**width

    # Force the computed sum to equal the target, bit by bit.
    for j in range(width):
        if (target >> j) & 1:
            enc.add_clause([acc[j]])
        else:
            enc.add_clause([-acc[j]])

    return {"num_vars": enc.num_vars, "clauses": enc.clauses}
