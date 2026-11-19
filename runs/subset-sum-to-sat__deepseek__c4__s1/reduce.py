"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Introduce one boolean variable x_i per number a_i, meaning "a_i is chosen".
Build a boolean circuit (with a Tseitin CNF encoding) that computes

    S = sum_i x_i * a_i

using ripple-carry binary adders, then assert S == target by requiring that
every bit of S equals the corresponding bit of target.

The circuit has O(n * W) gates where W is the bit length of the total sum,
so the reduction is polynomial in the size of the input (n plus the bit
lengths of the numbers).  Gate semantics are enforced by the Tseitin clauses,
so the CNF is satisfiable iff some sub-list sums to the target.
"""

from __future__ import annotations


class _Circuit:
    """A tiny gate-level circuit builder with a Tseitin CNF encoding.

    Signals are either Python bools (constants) or non-zero int literals
    (positive = variable, negative = negated variable).  Gate methods
    simplify constant inputs so no clauses are wasted.
    """

    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[list[int]] = []

    def new_var(self) -> int:
        self.nvars += 1
        return self.nvars

    def NOT(self, a):
        if a is True:
            return False
        if a is False:
            return True
        return -a

    def AND(self, a, b):
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        if a == b:
            return a
        if a == -b:
            return False
        z = self.new_var()
        self.clauses.append([-z, a])
        self.clauses.append([-z, b])
        self.clauses.append([z, -a, -b])
        return z

    def OR(self, a, b):
        if a is True or b is True:
            return True
        if a is False:
            return b
        if b is False:
            return a
        if a == b:
            return a
        if a == -b:
            return True
        z = self.new_var()
        self.clauses.append([z, -a])
        self.clauses.append([z, -b])
        self.clauses.append([-z, a, b])
        return z

    def XOR(self, a, b):
        if a is False:
            return b
        if a is True:
            return self.NOT(b)
        if b is False:
            return a
        if b is True:
            return self.NOT(a)
        if a == b:
            return False
        if a == -b:
            return True
        z = self.new_var()
        self.clauses.append([a, b, -z])
        self.clauses.append([-a, -b, -z])
        self.clauses.append([a, -b, z])
        self.clauses.append([-a, b, z])
        return z

    def add(self, a_bits, b_bits):
        """Ripple-carry addition of two equal-length little-endian bit lists."""
        carry = False
        out = []
        for a, b in zip(a_bits, b_bits):
            axb = self.XOR(a, b)
            out.append(self.XOR(axb, carry))
            carry = self.OR(self.AND(a, b), self.AND(carry, axb))
        return out


def _unsat() -> dict:
    return {"num_vars": 0, "clauses": [[]]}


def _sat() -> dict:
    return {"num_vars": 0, "clauses": []}


def reduce(instance: dict) -> dict:
    numbers = instance["numbers"]
    target = instance["target"]

    # Edge cases from the Subset Sum definition.
    if target < 0:
        return _unsat()
    if target == 0:
        return _sat()

    total = sum(numbers)
    if total < target:
        return _unsat()

    n = len(numbers)
    c = _Circuit()
    xs = [c.new_var() for _ in range(n)]

    # Width large enough to hold the total sum (and the target) without
    # overflow.  The extra bit makes the final carry a constant False.
    width = max(total.bit_length(), target.bit_length()) + 1

    acc = [False] * width
    for i, a in enumerate(numbers):
        contribution = [
            xs[i] if (a >> j) & 1 else False for j in range(width)
        ]
        acc = c.add(acc, contribution)

    # Require acc == target bit by bit.
    eq = True
    for j in range(width):
        bit = acc[j]
        want = (target >> j) & 1
        eq = c.AND(eq, bit if want else c.NOT(bit))

    if eq is False:
        c.clauses.append([])
    elif eq is not True:
        c.clauses.append([eq])

    return {"num_vars": c.nvars, "clauses": c.clauses}
