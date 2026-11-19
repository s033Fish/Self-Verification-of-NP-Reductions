"""Polynomial-time reduction from Subset Sum to SAT.

SOURCE (Subset Sum): {"numbers": [a1, a2, ...], "target": t}
    numbers are non-negative ints (may repeat); t is any int.
    Yes iff some sub-list sums to exactly t.

TARGET (SAT): {"num_vars": m, "clauses": [[literal, ...], ...]}
    Variables 1..m; literal +v / -v.  Yes iff some assignment satisfies
    every clause.

Construction
------------
For each number a_i we introduce a selection variable x_i (x_i true means
a_i is taken).  We then build a ripple-carry binary adder circuit, in CNF
via a Tseitin encoding, that computes

        acc = sum_i (x_i * a_i)

one number at a time.  The accumulator starts at 0 and has B bits, where
B = (sum of all numbers).bit_length(); every reachable sum is < 2^B, so B
bits suffice.  Finally we assert acc == target bit by bit.

The circuit is deterministic in the x_i, so the formula is satisfiable iff
some choice of numbers sums to target.

Trivial cases:
    t < 0                  -> unsatisfiable formula
    t = 0                  -> satisfiable formula (empty sub-list)
    t > sum(numbers)       -> unsatisfiable formula

The construction uses O(n * B) variables and clauses, i.e. polynomial in
the encoding length of the instance.  No brute-force solver is invoked.
"""

from __future__ import annotations


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # --- Trivial cases -------------------------------------------------
    if target < 0:
        # No sub-list can sum to a negative target.
        return {"num_vars": 0, "clauses": [[]]}  # unsatisfiable

    if target == 0:
        # The empty sub-list always sums to 0.
        return {"num_vars": 0, "clauses": []}  # satisfiable

    total = sum(numbers)
    if target > total:
        # Every sub-list sums to at most total.
        return {"num_vars": 0, "clauses": [[]]}  # unsatisfiable

    # --- Tseitin circuit builder --------------------------------------
    num_vars = 0
    clauses = []

    def new_var():
        nonlocal num_vars
        num_vars += 1
        return num_vars

    def add_clause(*literals):
        clauses.append(list(literals))

    # A variable forced to false, used for constant 0 bits.
    false_var = new_var()
    add_clause(-false_var)

    def xor2(a, b):
        """New variable equal to a XOR b."""
        out = new_var()
        add_clause(a, b, -out)
        add_clause(a, -b, out)
        add_clause(-a, b, out)
        add_clause(-a, -b, -out)
        return out

    def and2(a, b):
        """New variable equal to a AND b."""
        out = new_var()
        add_clause(-a, -b, out)
        add_clause(a, -out)
        add_clause(b, -out)
        return out

    def or2(a, b):
        """New variable equal to a OR b."""
        out = new_var()
        add_clause(a, b, -out)
        add_clause(-a, out)
        add_clause(-b, out)
        return out

    def full_adder(p, q, r):
        """Return (sum, carry) for the one-bit sum p + q + r."""
        t = xor2(p, q)
        s = xor2(t, r)
        u1 = and2(p, q)
        u2 = and2(p, r)
        u3 = and2(q, r)
        v = or2(u1, u2)
        c = or2(v, u3)
        return s, c

    # B bits are enough to hold every reachable sum (all < 2^B).
    B = total.bit_length()

    # Selection variable per number.
    select = [new_var() for _ in numbers]

    # Accumulator, initially zero.
    acc = [false_var] * B

    for i, a in enumerate(numbers):
        carry = false_var
        new_acc = []
        for j in range(B):
            p = acc[j]
            q = select[i] if (a >> j) & 1 else false_var
            s, carry = full_adder(p, q, carry)
            new_acc.append(s)
        # The final carry out of the top bit is always 0 because the sum is
        # at most `total` < 2^B; assert it for safety.
        add_clause(-carry)
        acc = new_acc

    # Assert accumulator == target, bit by bit.
    for j in range(B):
        if (target >> j) & 1:
            add_clause(acc[j])
        else:
            add_clause(-acc[j])

    return {"num_vars": num_vars, "clauses": clauses}
