"""Polynomial-time reduction from Subset Sum to SAT.

For an instance {"numbers": [a_1, ..., a_n], "target": t} we introduce one
boolean variable x_i per number (x_i is true iff a_i is selected) and build a
ripple-carry adder circuit that computes

    S = sum_i x_i * a_i

in binary.  The circuit is translated to CNF with the standard Tseitin
transform (every gate gets a fresh variable and clauses enforcing the gate's
truth table), and unit clauses force the bits of S to equal the bits of t.

The formula is satisfiable exactly when some subset of the numbers sums to t.
The circuit has O(n * W) gates where W = O(log(sum(numbers))) is the number of
bits needed for any subset sum, so the reduction is polynomial in the input
size (which counts the bit lengths of the numbers).
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # --- Trivial cases -------------------------------------------------
    # t < 0 is always no.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}
    # t = 0 is always yes (empty sub-list).
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    # No subset can reach a target larger than the sum of all numbers.
    if target > total:
        return {"num_vars": 0, "clauses": [[]]}

    # Enough bits to represent every possible subset sum (0..total).
    width = total.bit_length()

    num_vars = 0
    clauses = []

    def fresh():
        nonlocal num_vars
        num_vars += 1
        return num_vars

    # A "signal" is either a positive variable id (meaning that variable is
    # true) or None (meaning the constant false).  All circuit signals are
    # positive variables, so the helpers below only deal with those.

    def mk_and(a, b):
        if a is None or b is None:
            return None
        if a == b:
            return a
        z = fresh()
        clauses.append([-a, -b, z])   # a & b -> z
        clauses.append([a, -z])       # z -> a
        clauses.append([b, -z])       # z -> b
        return z

    def mk_xor(a, b):
        if a is None:
            return b
        if b is None:
            return a
        if a == b:
            return None
        z = fresh()
        clauses.append([-a, -b, -z])
        clauses.append([a, b, -z])
        clauses.append([a, -b, z])
        clauses.append([-a, b, z])
        return z

    def mk_or(a, b):
        if a is None:
            return b
        if b is None:
            return a
        if a == b:
            return a
        z = fresh()
        clauses.append([a, b, -z])
        clauses.append([-a, z])
        clauses.append([-b, z])
        return z

    def full_adder(a, b, carry):
        """Return (sum_bit, carry_out) for a + b + carry."""
        s = mk_xor(mk_xor(a, b), carry)
        # carry_out = (a & b) | (carry & (a ^ b))
        c_out = mk_or(mk_and(a, b), mk_and(carry, mk_xor(a, b)))
        return s, c_out

    # Accumulator bits, least significant first; starts at 0.
    acc = [None] * width

    for value in numbers:
        x = fresh()  # true iff this number is selected
        carry = None
        for k in range(width):
            addend = x if (value >> k) & 1 else None
            acc[k], carry = full_adder(acc[k], addend, carry)
        # The carry out of the top bit is always 0 because total < 2**width.

    # Force the computed sum to equal the target, bit by bit.
    for k in range(width):
        if (target >> k) & 1:
            if acc[k] is None:
                # This bit is constantly false, so the target is unreachable.
                clauses.append([])
            else:
                clauses.append([acc[k]])
        else:
            if acc[k] is not None:
                clauses.append([-acc[k]])

    return {"num_vars": num_vars, "clauses": clauses}
