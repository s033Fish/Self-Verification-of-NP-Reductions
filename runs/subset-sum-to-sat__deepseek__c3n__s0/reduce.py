"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
An instance of Subset Sum is  numbers = [a_1, ..., a_n], target t.
Introduce one boolean variable x_i for each number, meaning "a_i is chosen".
We must have  sum_i a_i * x_i == t.

This is a single linear equation with 0/1 coefficients.  We encode it with a
ripple-carry binary adder circuit (Tseitin transformation):

  * s_0 = 0
  * s_i = s_{i-1} + a_i * x_i        (i = 1..n)
  * require s_n == t

All partial sums are at most S = sum(a_i), so W = bit_length(S) bits suffice
(2^W > S, hence no overflow ever happens).  Each full-adder is encoded with
CNF clauses over fresh Tseitin variables.  The result uses O(n * W) variables
and clauses, i.e. polynomial in the size of the input.

Edge cases are handled directly:
  * t < 0            -> unsatisfiable formula (empty clause)
  * t == 0           -> satisfiable formula (empty subset)
  * t > sum(numbers) -> unsatisfiable formula
"""

from __future__ import annotations


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]
    n = len(numbers)
    total = sum(numbers)

    # ---- trivial cases -------------------------------------------------
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}      # always no
    if target == 0:
        return {"num_vars": 0, "clauses": []}        # empty subset, always yes
    if target > total:
        return {"num_vars": 0, "clauses": [[]]}      # can never reach it

    W = total.bit_length()                            # 2**W > total

    clauses: list[list[int]] = []
    counter = [0]

    def new_var() -> int:
        counter[0] += 1
        return counter[0]

    # ---- gate helpers (constants are represented by None = false) ------
    def xor2(a, b):
        if a is None:
            return b
        if b is None:
            return a
        if a == b:
            return None
        z = new_var()
        clauses.append([a, b, -z])
        clauses.append([a, -b, z])
        clauses.append([-a, b, z])
        clauses.append([-a, -b, -z])
        return z

    def xor3(a, b, c):
        return xor2(xor2(a, b), c)

    def and2(a, b):
        if a is None or b is None:
            return None
        if a == b:
            return a
        z = new_var()
        clauses.append([-a, -b, z])   # a and b -> z
        clauses.append([a, -z])       # z -> a
        clauses.append([b, -z])       # z -> b
        return z

    def majority(a, b, c):
        vals = []
        for v in (a, b, c):
            if v is not None and v not in vals:
                vals.append(v)
        if len(vals) == 0:
            return None
        if len(vals) == 1:
            # majority(a, 0, 0) = 0
            return None
        if len(vals) == 2:
            return and2(vals[0], vals[1])
        a, b, c = vals
        z = new_var()
        clauses.append([-a, -b, z])
        clauses.append([-a, -c, z])
        clauses.append([-b, -c, z])
        clauses.append([a, b, -z])
        clauses.append([a, c, -z])
        clauses.append([b, c, -z])
        return z

    # ---- choice variables and addend bits ------------------------------
    x = [new_var() for _ in range(n)]

    # addend[i][j] is a variable that is true iff (a_i bit j is 1) and x_i.
    addend = []
    for i in range(n):
        row = []
        for j in range(W):
            p = new_var()
            if (numbers[i] >> j) & 1:
                clauses.append([-p, x[i]])
                clauses.append([p, -x[i]])
            else:
                clauses.append([-p])          # force p = false
            row.append(p)
        addend.append(row)

    # ---- ripple-carry addition -----------------------------------------
    s_prev = [None] * W                        # s_0 = 0
    for i in range(n):
        s_cur = [None] * W
        carry = None
        for j in range(W):
            a = s_prev[j]
            b = addend[i][j]
            cin = carry
            s_cur[j] = xor3(a, b, cin)
            carry = majority(a, b, cin)
        s_prev = s_cur

    # ---- require s_n == target -----------------------------------------
    for j in range(W):
        bit = (target >> j) & 1
        v = s_prev[j]
        if bit:
            clauses.append([] if v is None else [v])
        else:
            if v is not None:
                clauses.append([-v])

    return {"num_vars": counter[0], "clauses": clauses}
