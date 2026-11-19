"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Given numbers a_1..a_n and target t, introduce a Boolean variable x_i for
"number a_i is chosen".  The chosen sum is

    S = sum_i a_i * x_i

which we compute with a ripple-carry binary adder circuit built out of
AND / OR / XOR gates.  Each a_i * x_i is a W-bit constant vector whose j-th
bit is x_i when bit j of a_i is set, else the constant 0.  The numbers are
accumulated one at a time.  Finally we assert S == t bit by bit.

The circuit is translated to CNF with the standard Tseitin transformation
(one auxiliary variable per gate, constant-size clause set per gate).  The
number of bits W is O(log(sum a_i)), so the whole construction is polynomial
in the size of the input.

Edge cases:
  * t < 0  -> unsatisfiable formula (empty clause).
  * t == 0 -> satisfiable formula (no clauses); the empty sub-list works.
  * t > sum(numbers) is handled by the bit comparison / overflow check.
"""

from __future__ import annotations

from typing import Any


class _Circuit:
    """Tseitin circuit builder over CNF variables 1..num_vars.

    A "bit" is either an int (a variable index >= 1) or a Python bool
    constant (True/False).
    """

    def __init__(self) -> None:
        self.num_vars = 0
        self.clauses: list[list[int]] = []

    def new_var(self) -> int:
        self.num_vars += 1
        return self.num_vars

    def add_clause(self, clause: list[int]) -> None:
        self.clauses.append(list(clause))

    @staticmethod
    def _is_const(bit: Any) -> bool:
        return isinstance(bit, bool)

    def AND(self, a: Any, b: Any) -> Any:
        if a is True:
            return b
        if b is True:
            return a
        if a is False or b is False:
            return False
        z = self.new_var()
        self.add_clause([-z, a])
        self.add_clause([-z, b])
        self.add_clause([-a, -b, z])
        return z

    def OR(self, a: Any, b: Any) -> Any:
        if a is False:
            return b
        if b is False:
            return a
        if a is True or b is True:
            return True
        z = self.new_var()
        self.add_clause([z, -a])
        self.add_clause([z, -b])
        self.add_clause([-z, a, b])
        return z

    def NOT(self, a: Any) -> Any:
        if a is True:
            return False
        if a is False:
            return True
        z = self.new_var()
        self.add_clause([a, z])
        self.add_clause([-a, -z])
        return z

    def XOR(self, a: Any, b: Any) -> Any:
        if self._is_const(a) and self._is_const(b):
            return bool(a) ^ bool(b)
        if self._is_const(a):
            return self.NOT(b) if a else b
        if self._is_const(b):
            return self.NOT(a) if b else a
        z = self.new_var()
        self.add_clause([-a, -b, -z])
        self.add_clause([a, b, -z])
        self.add_clause([a, -b, z])
        self.add_clause([-a, b, z])
        return z

    def full_adder(self, a: Any, b: Any, carry_in: Any) -> tuple[Any, Any]:
        s = self.XOR(self.XOR(a, b), carry_in)
        carry_out = self.OR(
            self.AND(a, b),
            self.OR(self.AND(a, carry_in), self.AND(b, carry_in)),
        )
        return s, carry_out


def _ripple_add(circ: _Circuit, a_bits: list[Any], b_bits: list[Any]) -> list[Any]:
    """Add two little-endian bit vectors, returning the low bits (carry out dropped)."""
    result: list[Any] = []
    carry: Any = False
    for a_bit, b_bit in zip(a_bits, b_bits):
        total, carry = circ.full_adder(a_bit, b_bit, carry)
        result.append(total)
    return result


def reduce(instance: dict) -> dict:
    """Reduce a Subset Sum instance to a SAT instance."""
    numbers = instance["numbers"]
    target = instance["target"]

    # t < 0: impossible, emit an unsatisfiable formula.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # t == 0: the empty sub-list works, emit a trivially satisfiable formula.
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    # W bits are enough to hold any partial sum without overflow: total < 2**W.
    W = max(1, total.bit_length()) + 1

    circ = _Circuit()
    x = [circ.new_var() for _ in numbers]

    acc: list[Any] = [False] * W
    for var, number in zip(x, numbers):
        term = [var if (number >> j) & 1 else False for j in range(W)]
        acc = _ripple_add(circ, acc, term)

    if target >> W:
        # target cannot fit in W bits while every sum does, so it is unreachable.
        circ.add_clause([])
    else:
        for j in range(W):
            target_bit = (target >> j) & 1
            sum_bit = acc[j]
            if target_bit == 1:
                if sum_bit is False:
                    circ.add_clause([])
                elif sum_bit is not True:
                    circ.add_clause([sum_bit])
            else:
                if sum_bit is True:
                    circ.add_clause([])
                elif sum_bit is not False:
                    circ.add_clause([-sum_bit])

    return {"num_vars": circ.num_vars, "clauses": circ.clauses}
