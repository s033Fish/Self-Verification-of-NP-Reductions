"""Polynomial-time reduction from Subset Sum to SAT (CNF).

Given a Subset Sum instance {"numbers": [...], "target": t} we build a CNF
formula whose variables are:

  * x_i    for i = 1..n   (x_i means "number i is chosen")
  * zero   a variable forced to false (used as a constant)
  * gate variables introduced by Tseitin's transformation for a ripple-carry
    binary adder that computes  sum_i a_i * x_i.

The adder is built from full adders.  After all n numbers have been added the
accumulator bits are forced to equal the binary representation of t.  Hence the
formula is satisfiable iff some subset of the numbers sums to t.

The construction is polynomial: with B = bit length of the largest number the
adder has L = O(B + log n) bits and uses O(n * L) gates, each encoded with a
constant number of clauses.

Signals are represented as integers: 0 means the constant false, a positive
integer v means the variable v.  Gates are encoded generically by enumerating
the assignments of their (at most three) distinct input variables, which makes
the encoding correct even when inputs are aliased (the same variable appearing
in several positions) or constant.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # --- trivial cases -------------------------------------------------
    if target < 0:
        # unsatisfiable formula: one empty clause
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        # always yes (empty subset): satisfiable formula with no clauses
        return {"num_vars": 0, "clauses": []}
    if not numbers:
        # target > 0 and no numbers: impossible
        return {"num_vars": 0, "clauses": [[]]}

    num_vars = 0
    clauses = []

    def new_var():
        nonlocal num_vars
        num_vars += 1
        return num_vars

    def add(clause):
        clauses.append(list(clause))

    zero = new_var()
    add([-zero])  # constant false

    n = len(numbers)
    xs = [new_var() for _ in range(n)]

    max_sum = sum(numbers)
    L = max(max_sum.bit_length(), target.bit_length(), 1) + 1

    def add_gate(inputs, out, func):
        """Tseitin-encode  out <-> func(*inputs).

        ``inputs`` may contain 0 (constant false) and repeated variables; the
        encoding enumerates assignments of the distinct input variables, so it
        stays correct under aliasing.
        """
        distinct = sorted({v for v in inputs if v != 0})
        k = len(distinct)
        for mask in range(1 << k):
            values = {distinct[i]: (mask >> i) & 1 for i in range(k)}
            args = [(values[v] if v != 0 else 0) for v in inputs]
            f = 1 if func(*args) else 0
            clause = [(-v if values[v] else v) for v in distinct]
            # forbid  out == 1 - f
            clause.append(-out if f == 0 else out)
            add(clause)

    def xor3(a, b, c):
        return (a + b + c) % 2

    def majority(a, b, c):
        return 1 if a + b + c >= 2 else 0

    acc = [0] * L  # accumulator, starts at 0 (constant false)

    for i in range(n):
        a = numbers[i]
        x = xs[i]
        if a == 0:
            continue  # adding zero changes nothing
        carry = 0
        new_acc = []
        for j in range(L):
            b = x if (a >> j) & 1 else 0
            s = new_var()
            cout = new_var()
            add_gate([acc[j], b, carry], s, xor3)
            add_gate([acc[j], b, carry], cout, majority)
            new_acc.append(s)
            carry = cout
        if carry != 0:
            add([-carry])  # no overflow: running sum <= max_sum < 2**L
        acc = new_acc

    for j in range(L):
        bit = (target >> j) & 1
        if bit:
            if acc[j] == 0:
                add([])  # impossible to set a constant-false bit
            else:
                add([acc[j]])
        else:
            if acc[j] != 0:
                add([-acc[j]])

    return {"num_vars": num_vars, "clauses": clauses}
