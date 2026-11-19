"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Given numbers a_1..a_n >= 0 and target t, build a Boolean circuit that
computes the sum of the chosen numbers in binary and forces it to equal t.

* One selection variable s_i per number (s_i true  <=>  a_i is chosen).
* The chosen value of a_i is p_i = s_i * a_i, computed bitwise: bit j of
  p_i is (s_i AND bit_j(a_i)), which is just s_i when the bit is 1 and
  constant false when it is 0.
* A ripple-carry adder accumulates the p_i into a running sum of width W,
  where W = bit_length(sum(a_i)).  Every subset sum is <= sum(a_i) < 2^W,
  so the final carry out is forced to 0.
* Unit clauses force each bit of the running sum to equal the
  corresponding bit of t.

All gates are encoded with Tseitin clauses (equivalences), so the formula
is satisfiable exactly when some subset sums to t.  The size is
O(n * W) gates/clauses and W is polynomial in the input bit length, hence
the reduction is polynomial time.
"""

from __future__ import annotations

from typing import Any


def _unsat() -> dict:
    """A formula that is never satisfiable (empty clause)."""
    return {"num_vars": 0, "clauses": [[]]}


def _sat() -> dict:
    """A formula that is always satisfiable (no clauses)."""
    return {"num_vars": 0, "clauses": []}


def reduce(instance: dict) -> dict:
    """Reduce a Subset Sum instance to a SAT instance.

    instance: {"numbers": [...], "target": t}
    returns:  {"num_vars": m, "clauses": [[literal, ...], ...]}
    """
    numbers = list(instance["numbers"])
    target = instance["target"]

    # ---- Source edge cases -------------------------------------------
    if target < 0:
        return _unsat()
    if target == 0:
        # The empty sub-list always works.
        return _sat()

    total = sum(numbers)
    if target > total:
        # No subset can reach the target.
        return _unsat()

    # Now 0 < target <= total, so total > 0 and W >= 1.
    W = total.bit_length()  # every subset sum is < 2**W

    clauses: list[list[int]] = []
    counter = [0]

    def new_var() -> int:
        counter[0] += 1
        return counter[0]

    # Constant variables.
    FALSE = new_var()
    clauses.append([-FALSE])
    TRUE = new_var()
    clauses.append([TRUE])

    # ---- Gate helpers (Tseitin equivalences) --------------------------
    def NOT(a: int) -> int:
        if a == FALSE:
            return TRUE
        if a == TRUE:
            return FALSE
        z = new_var()
        clauses.append([a, z])
        clauses.append([-a, -z])
        return z

    def AND(a: int, b: int) -> int:
        if a == FALSE or b == FALSE:
            return FALSE
        if a == TRUE:
            return b
        if b == TRUE:
            return a
        if a == b:
            return a
        z = new_var()
        clauses.append([-a, -b, z])
        clauses.append([a, -z])
        clauses.append([b, -z])
        return z

    def OR(a: int, b: int) -> int:
        if a == TRUE or b == TRUE:
            return TRUE
        if a == FALSE:
            return b
        if b == FALSE:
            return a
        if a == b:
            return a
        z = new_var()
        clauses.append([a, b, -z])
        clauses.append([-a, z])
        clauses.append([-b, z])
        return z

    def XOR(a: int, b: int) -> int:
        if a == FALSE:
            return b
        if b == FALSE:
            return a
        if a == TRUE:
            return NOT(b)
        if b == TRUE:
            return NOT(a)
        if a == b:
            return FALSE
        z = new_var()
        clauses.append([a, b, -z])
        clauses.append([a, -b, z])
        clauses.append([-a, b, z])
        clauses.append([-a, -b, -z])
        return z

    def MAJ(a: int, b: int, c: int) -> int:
        return OR(AND(a, b), OR(AND(a, c), AND(b, c)))

    def full_adder(a: int, b: int, cin: int):
        """Return (sum_bit, carry_out) for a + b + cin."""
        t = XOR(a, b)
        s = XOR(t, cin)
        cout = OR(AND(a, b), AND(t, cin))
        return s, cout

    # ---- Accumulate the chosen numbers --------------------------------
    acc = [FALSE] * W
    for value in numbers:
        sel = new_var()  # s_i: is this number chosen?
        # p_i = sel * value, bit by bit.
        p = [sel if (value >> j) & 1 else FALSE for j in range(W)]
        carry = FALSE
        new_acc = []
        for j in range(W):
            s_bit, carry = full_adder(acc[j], p[j], carry)
            new_acc.append(s_bit)
        # Final carry must be 0 (the true sum fits in W bits).
        clauses.append([-carry])
        acc = new_acc

    # ---- Force the accumulated sum to equal target --------------------
    for j in range(W):
        if (target >> j) & 1:
            clauses.append([acc[j]])
        else:
            clauses.append([-acc[j]])

    return {"num_vars": counter[0], "clauses": clauses}
