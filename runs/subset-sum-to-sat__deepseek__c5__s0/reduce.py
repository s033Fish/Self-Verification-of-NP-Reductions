"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
For an instance with numbers a_1..a_n and target t, introduce one boolean
variable x_i meaning "number i is chosen".  We must express

    sum_i x_i * a_i == t.

This is done with a ripple-carry binary adder built from full adders.  The
accumulator after processing the first i numbers is kept in bits
s[i][0..B-1]; c[i][j] is the carry into bit j while adding number i.  Each
full adder is encoded by forbidding every (inputs, outputs) combination that
is not a valid full-adder row.  Finally the accumulator bits are forced to
equal the bits of t and the final carry is forced to 0.

All sizes are polynomial in the input length: B = O(bitlength(sum a_i)) and
there are O(n*B) full adders, each with a constant number of clauses.
"""

from __future__ import annotations


def _unsat():
    # An empty clause can never be satisfied.
    return {"num_vars": 0, "clauses": [[]]}


def _sat():
    # No clauses: trivially satisfiable.
    return {"num_vars": 0, "clauses": []}


def reduce(instance):
    numbers = instance["numbers"]
    t = instance["target"]
    n = len(numbers)

    # --- trivial cases (part of the reduction, not a search) -------------
    if t < 0:
        return _unsat()
    total = sum(numbers)
    if t > total:
        return _unsat()
    if n == 0:
        # total == 0 and 0 <= t <= total, so t == 0 -> yes.
        return _sat()

    B = max(1, total.bit_length())  # enough bits for any achievable sum

    clauses = []
    nv = 0

    def new_var():
        nonlocal nv
        nv += 1
        return nv

    # x[i-1] is true iff numbers[i-1] is selected
    x = [new_var() for _ in range(n)]

    # s[i][j]: bit j of the sum of the first i numbers (i = 0 is constant 0)
    s = [[None] * B for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(B):
            s[i][j] = new_var()

    # c[i][j]: carry into bit j while adding number i.
    # c[i][0] is constant 0; c[i][B] is the carry out.
    c = [[None] * (B + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, B + 1):
            c[i][j] = new_var()

    def add_full_adder(a, b, cin, sout, cout):
        """Encode one full adder.

        a, b, cin are either None (constant 0) or a positive variable index.
        sout, cout are positive variable indices.  We add a clause excluding
        every assignment that is not a valid full-adder row.
        """
        for av in (0, 1):
            if a is None and av == 1:
                continue
            for bv in (0, 1):
                if b is None and bv == 1:
                    continue
                for cv in (0, 1):
                    if cin is None and cv == 1:
                        continue
                    total_in = av + bv + cv
                    valid_s = total_in & 1
                    valid_cout = 1 if total_in >= 2 else 0
                    for sv in (0, 1):
                        for cov in (0, 1):
                            if sv == valid_s and cov == valid_cout:
                                continue
                            clause = []
                            if a is not None:
                                clause.append(-a if av == 1 else a)
                            if b is not None:
                                clause.append(-b if bv == 1 else b)
                            if cin is not None:
                                clause.append(-cin if cv == 1 else cin)
                            clause.append(-sout if sv == 1 else sout)
                            clause.append(-cout if cov == 1 else cout)
                            clauses.append(clause)

    for i in range(1, n + 1):
        ai = numbers[i - 1]
        for j in range(B):
            a = s[i - 1][j]          # accumulator bit (None when i-1 == 0)
            b = x[i - 1] if (ai >> j) & 1 else None
            cin = c[i][j] if j >= 1 else None
            add_full_adder(a, b, cin, s[i][j], c[i][j + 1])

    # The final carry must be zero (sum < 2**B).
    clauses.append([-c[n][B]])

    # Force the accumulator to equal t bit by bit.
    for j in range(B):
        if (t >> j) & 1:
            clauses.append([s[n][j]])
        else:
            clauses.append([-s[n][j]])

    return {"num_vars": nv, "clauses": clauses}
