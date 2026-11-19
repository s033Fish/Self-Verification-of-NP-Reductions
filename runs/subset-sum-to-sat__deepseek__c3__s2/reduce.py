"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
Given numbers a_1..a_n and target t, introduce a selection variable x_i for
each number (x_i true means "take a_i").  We then build, with a ripple-carry
adder, the partial sums

    S_0 = 0,   S_i = S_{i-1} + x_i * a_i      (i = 1..n)

as m-bit binary numbers, and require S_n = t bit by bit.  Each full adder is
encoded exactly in CNF, so a satisfying assignment of the formula exists iff
some sub-list of the numbers sums to t.

Sizes: m = O(log(sum a_i)) and there are O(n*m) adders, so the formula has
O(n*m) variables and clauses -- polynomial in the input size.

Edge cases (matching the SubsetSum spec):
  * t < 0  -> always no: emit an unsatisfiable formula (one empty clause).
  * t = 0  -> always yes: emit the empty formula (satisfiable).
  * t > sum(numbers) -> no: emit an unsatisfiable formula.
"""

from __future__ import annotations

from typing import Any


def _is_const(sig: Any) -> bool:
    """A signal is a constant iff it is a Python bool (not an int literal)."""
    return isinstance(sig, bool)


def _full_adder(clauses, a, b, cin, new_var):
    """Encode an exact full adder.

    Inputs a, b, cin are signals: either an int literal (meaning the value of
    that literal) or a bool constant.  Creates two fresh variables for the sum
    and carry-out, appends the defining clauses, and returns (sum, carry).

    For every combination of input values consistent with the constants we
    add the clause "inputs take these values => output takes its value".
    """
    s = new_var()
    c = new_var()
    for av in (False, True):
        for bv in (False, True):
            for cv in (False, True):
                lits = []
                consistent = True
                for sig, val in ((a, av), (b, bv), (cin, cv)):
                    if _is_const(sig):
                        if sig != val:
                            consistent = False
                            break
                    else:
                        # literal that is true when sig == val
                        lits.append(sig if val else -sig)
                if not consistent:
                    continue
                sum_val = av ^ bv ^ cv
                carry_val = (av and bv) or (av and cv) or (bv and cv)
                # clause: "some input differs from its value, OR output is right"
                neg = [-lit for lit in lits]
                clauses.append(neg + [s if sum_val else -s])
                clauses.append(neg + [c if carry_val else -c])
    return s, c


def _force_false(clauses, sig):
    """Add clauses forcing signal `sig` to be false."""
    if _is_const(sig):
        if sig:
            clauses.append([])  # unsatisfiable
    else:
        clauses.append([-sig])


def _force_true(clauses, sig):
    """Add clauses forcing signal `sig` to be true."""
    if _is_const(sig):
        if not sig:
            clauses.append([])  # unsatisfiable
    else:
        clauses.append([sig])


def _unsat():
    return {"num_vars": 0, "clauses": [[]]}


def _sat():
    return {"num_vars": 0, "clauses": []}


def reduce(instance):
    """Reduce a SubsetSum instance to a Sat instance (both plain dicts)."""
    numbers = list(instance["numbers"])
    target = instance["target"]

    # --- Edge cases -----------------------------------------------------
    if target < 0:
        return _unsat()
    if target == 0:
        return _sat()
    total = sum(numbers)
    if target > total:
        return _unsat()

    # --- Bit width: enough that no partial sum ever overflows -------------
    m = max(total.bit_length(), target.bit_length()) + 1

    clauses: list[list[int]] = []
    counter = [0]

    def new_var() -> int:
        counter[0] += 1
        return counter[0]

    # One selection variable per number.
    select = [new_var() for _ in numbers]

    # S_prev holds the bits of the running sum; S_0 = 0 (all constants False).
    s_prev: list[Any] = [False] * m

    for i, a in enumerate(numbers):
        carry: Any = False  # carry into bit 0 is 0
        s_cur: list[Any] = [None] * m
        for j in range(m):
            p = s_prev[j]
            # bit j of x_i * a_i: x_i when a has bit j set, else 0
            q = select[i] if (a >> j) & 1 else False
            s_cur[j], carry = _full_adder(clauses, p, q, carry, new_var)
        # No overflow is possible, so the top carry-out must be 0.
        _force_false(clauses, carry)
        s_prev = s_cur

    # Require the final sum to equal the target, bit by bit.
    for j in range(m):
        bit = (target >> j) & 1
        if bit:
            _force_true(clauses, s_prev[j])
        else:
            _force_false(clauses, s_prev[j])

    return {"num_vars": counter[0], "clauses": clauses}
