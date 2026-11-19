"""Polynomial-time reduction from Subset Sum to SAT.

Instance in : {"numbers": [a1, a2, ...], "target": t}   (Subset Sum)
Instance out: {"num_vars": m, "clauses": [[literal, ...], ...]}   (SAT)

Idea
----
Introduce one Boolean variable x_i for every number a_i, meaning "a_i is
part of the chosen sub-list".  Build a Boolean circuit that computes the
binary value of the sum  sum_i a_i * x_i  with a ripple-carry adder that
adds the numbers one at a time, then force every bit of the result to
equal the corresponding bit of t.  The circuit is converted to CNF with
the standard Tseitin encoding (one fresh variable per gate).

If W is the bit length of the total sum, the circuit has O(n * W) gates
and each gate becomes at most four clauses, so the reduction is polynomial
in the length of the input.

Edge cases (from the Subset Sum specification):
  * t < 0  -> always no  -> emit the empty clause.
  * t = 0  -> always yes -> emit the empty CNF.
  * t > sum(numbers) -> unreachable -> emit the empty clause.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]

    # --- Edge cases ------------------------------------------------------
    if target < 0:
        # No sub-list can sum to a negative target.
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        # The empty sub-list always sums to zero.
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    if target > total:
        # Even taking every number is not enough.
        return {"num_vars": 0, "clauses": [[]]}

    # --- CNF builder -----------------------------------------------------
    clauses = []

    counter = [0]

    def new_var():
        counter[0] += 1
        return counter[0]

    def add_clause(*literals):
        clauses.append(list(literals))

    # Constant literals.  TRUE_LIT is always true, FALSE_LIT always false.
    true_var = new_var()
    false_var = new_var()
    add_clause(true_var)      # true_var = true
    add_clause(-false_var)    # false_var = false
    TRUE_LIT = true_var
    FALSE_LIT = false_var

    # Tseitin gates.  Inputs and outputs are signed literals; a fresh
    # variable is created for every gate output.
    def gate_and(p, q):
        z = new_var()
        add_clause(-z, p)
        add_clause(-z, q)
        add_clause(z, -p, -q)
        return z

    def gate_or(p, q):
        z = new_var()
        add_clause(z, -p)
        add_clause(z, -q)
        add_clause(-z, p, q)
        return z

    def gate_xor(p, q):
        z = new_var()
        add_clause(-z, p, q)
        add_clause(-z, -p, -q)
        add_clause(z, -p, q)
        add_clause(z, p, -q)
        return z

    # Choice variables: x_i is true iff number i is selected.
    choice = [new_var() for _ in numbers]

    # Enough bits for the total sum (and hence for the target), plus one
    # guard bit so that no carry ever escapes the represented width.
    width = total.bit_length() + 1

    # Running partial sum, least significant bit first.  It starts at zero.
    partial = [FALSE_LIT] * width

    for i, value in enumerate(numbers):
        carry = FALSE_LIT
        new_partial = []
        for bit in range(width):
            # Bit `bit` of `value`, but only added when x_i is true.
            if (value >> bit) & 1:
                addend = choice[i]
            else:
                addend = FALSE_LIT

            # Full adder for this bit position:
            #   sum   = partial XOR addend XOR carry
            #   carry = majority(partial, addend, carry)
            t1 = gate_xor(partial[bit], addend)
            sum_bit = gate_xor(t1, carry)

            c1 = gate_and(partial[bit], addend)
            c2 = gate_and(partial[bit], carry)
            c3 = gate_and(addend, carry)
            carry = gate_or(gate_or(c1, c2), c3)

            new_partial.append(sum_bit)
        partial = new_partial

    # Force the computed sum to equal the target, bit by bit.
    for bit in range(width):
        if (target >> bit) & 1:
            add_clause(partial[bit])
        else:
            add_clause(-partial[bit])

    return {"num_vars": counter[0], "clauses": clauses}
