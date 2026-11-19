"""Polynomial-time reduction from Subset Sum to SAT.

For an instance ``{"numbers": [a1, ...], "target": t}`` we build a Boolean
circuit with one choice variable per number.  A ripple-carry adder adds
``x_i * a_i`` for every number, so the accumulator holds the sum of the
chosen numbers.  Unit clauses then force that accumulator to equal ``t``.
The circuit is turned into CNF with the standard Tseitin transformation.

The construction uses O(n * W) gates, where n is the number of numbers and
W is the bit length of their total sum, so it runs in polynomial time in
the size of the source instance.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    total = sum(numbers)

    # Trivial cases, handled directly to keep the circuit well formed.
    if target < 0 or target > total:
        # No sub-list can reach the target: unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        # The empty sub-list works: satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    num_vars = 0
    clauses = []

    def new_var():
        nonlocal num_vars
        num_vars += 1
        return num_vars

    def clause(*literals):
        clauses.append(list(literals))

    def const_false():
        v = new_var()
        clause(-v)
        return v

    def gate_and(a, b):
        z = new_var()
        clause(-z, a)
        clause(-z, b)
        clause(z, -a, -b)
        return z

    def gate_or(a, b):
        z = new_var()
        clause(z, -a)
        clause(z, -b)
        clause(-z, a, b)
        return z

    def gate_xor(a, b):
        z = new_var()
        clause(a, b, -z)
        clause(-a, -b, -z)
        clause(a, -b, z)
        clause(-a, b, z)
        return z

    def full_adder(a, b, carry_in):
        s = gate_xor(gate_xor(a, b), carry_in)
        ab = gate_and(a, b)
        ac = gate_and(a, carry_in)
        bc = gate_and(b, carry_in)
        carry_out = gate_or(gate_or(ab, ac), bc)
        return s, carry_out

    false = const_false()

    # total < 2**width, so width bits are enough for every partial sum.
    width = total.bit_length() + 1
    accumulator = [false] * width

    for number in numbers:
        choose = new_var()  # x_i: is this number part of the sub-list?
        addend = [
            choose if (number >> bit) & 1 else false
            for bit in range(width)
        ]
        carry = false
        for bit in range(width):
            summed_bit, carry = full_adder(accumulator[bit], addend[bit], carry)
            accumulator[bit] = summed_bit

    # Force the accumulator to equal the target, bit by bit.
    for bit in range(width):
        if (target >> bit) & 1:
            clause(accumulator[bit])
        else:
            clause(-accumulator[bit])

    return {"num_vars": num_vars, "clauses": clauses}
