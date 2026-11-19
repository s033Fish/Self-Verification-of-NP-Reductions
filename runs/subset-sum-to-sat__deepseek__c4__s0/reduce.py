"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Given numbers a_1..a_n and target t, introduce one boolean variable x_i per
number meaning "a_i is chosen".  The chosen sum is

    sum_i x_i * a_i

which we compute with a ripple-carry binary adder built out of full adders.
Every gate is Tseitin-encoded into CNF, so the formula is satisfiable exactly
when some choice of the x_i makes the computed sum equal to t.

The adder works on W = bit_length(sum(numbers)) bits, which is enough to hold
every possible subset sum.  If t < 0 or t > sum(numbers) the answer is
trivially no; if t == 0 the answer is trivially yes.  Otherwise the CNF is
built.  The number of variables and clauses is O(n * W), polynomial in the
input size (n plus the bit lengths of the numbers).
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    total = sum(numbers)

    # ---- trivial cases -------------------------------------------------
    if target < 0 or target > total:
        # unsatisfiable: a formula containing the empty clause
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        # empty sub-list works: satisfiable formula with no clauses
        return {"num_vars": 0, "clauses": []}

    # target > 0 and target <= total, so total >= 1
    W = total.bit_length()

    counter = 0
    clauses: list[list[int]] = []

    def new_var() -> int:
        nonlocal counter
        counter += 1
        return counter

    def add_clause(*lits: int) -> None:
        clauses.append(list(lits))

    # a variable forced to false, used as the constant 0 bit
    FALSE = new_var()
    add_clause(-FALSE)

    def xor(l1: int, l2: int) -> int:
        z = new_var()
        add_clause(-l1, -l2, -z)
        add_clause(l1, l2, -z)
        add_clause(l1, -l2, z)
        add_clause(-l1, l2, z)
        return z

    def majority(l1: int, l2: int, l3: int) -> int:
        z = new_var()
        add_clause(-l1, -l2, z)
        add_clause(-l1, -l3, z)
        add_clause(-l2, -l3, z)
        add_clause(l1, l2, -z)
        add_clause(l1, l3, -z)
        add_clause(l2, l3, -z)
        return z

    def full_adder(l1: int, l2: int, l3: int) -> tuple[int, int]:
        s = xor(xor(l1, l2), l3)
        c = majority(l1, l2, l3)
        return s, c

    # selection variables
    x = [new_var() for _ in range(n)]

    # accumulator bits, initially all zero
    acc = [FALSE] * W

    for i in range(n):
        a = numbers[i]
        # addend bits: bit j is x_i if a has bit j set, else constant 0
        addend = [(x[i] if (a >> j) & 1 else FALSE) for j in range(W)]
        carry = FALSE
        new_acc = []
        for j in range(W):
            s, carry = full_adder(acc[j], addend[j], carry)
            new_acc.append(s)
        # the sum can never exceed `total`, so there is no overflow
        add_clause(-carry)
        acc = new_acc

    # force the computed sum to equal the target, bit by bit
    for j in range(W):
        if (target >> j) & 1:
            add_clause(acc[j])
        else:
            add_clause(-acc[j])

    return {"num_vars": counter, "clauses": clauses}
