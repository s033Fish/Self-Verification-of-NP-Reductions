"""Polynomial-time reduction from Subset Sum to SAT.

The reduction builds a Boolean circuit that adds the selected numbers in
binary.  For each number a_i we introduce a selection variable x_i.  A
chain of full adders computes the n-bit partial sums; the final partial
sum is constrained to equal the target t bit by bit.

The circuit uses O(len(numbers) * n) variables and clauses, where n is
the bit length of max(target, sum(numbers)).  Since n is bounded by the
input length and len(numbers) is part of the input length, the reduction
is polynomial-time.
"""


def _add_full_adder(clauses, a, b, cin, s, cout):
    """Append CNF clauses for a full adder.

    Inputs and outputs are literals (nonzero ints).  The clauses enforce
    s == a XOR b XOR cin and cout == majority(a, b, cin).
    """
    # s == a XOR b XOR cin
    clauses.append([a, b, -cin, s])
    clauses.append([a, -b, cin, s])
    clauses.append([-a, b, cin, s])
    clauses.append([-a, -b, -cin, s])
    clauses.append([a, b, cin, -s])
    clauses.append([a, -b, -cin, -s])
    clauses.append([-a, b, -cin, -s])
    clauses.append([-a, -b, cin, -s])

    # cout == majority(a, b, cin)
    clauses.append([-a, -b, cout])
    clauses.append([-a, -cin, cout])
    clauses.append([-b, -cin, cout])
    clauses.append([a, b, -cout])
    clauses.append([a, cin, -cout])
    clauses.append([b, cin, -cout])


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # Negative targets are always no: emit an unsatisfiable empty clause.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    total = sum(numbers)
    # Enough bits for both the target and any possible subset sum.
    n = max(1, target.bit_length(), total.bit_length())

    clauses = []
    next_var = 0

    def new_var():
        nonlocal next_var
        next_var += 1
        return next_var

    # A variable forced false, used as the constant 0.
    false = new_var()
    clauses.append([-false])

    # x[i] is true iff numbers[i] is included in the subset.
    x = [new_var() for _ in numbers]

    # prev holds the n bits of the partial sum before the current number.
    prev = [false] * n

    for i, number in enumerate(numbers):
        # Little-endian bits of this number, as a string of '0'/'1'.
        bits = bin(number)[2:][::-1]
        cur = [0] * n
        carry = false  # carry into bit 0
        for j in range(n):
            bit = 1 if j < len(bits) and bits[j] == "1" else 0
            b = x[i] if bit else false
            s = new_var()
            cout = new_var()
            _add_full_adder(clauses, prev[j], b, carry, s, cout)
            cur[j] = s
            carry = cout
        # The partial sum is < 2**n, so the top carry must be 0.
        clauses.append([-carry])
        prev = cur

    # The final partial sum must equal the target, bit by bit.
    for j in range(n):
        if (target >> j) & 1:
            clauses.append([prev[j]])
        else:
            clauses.append([-prev[j]])

    return {"num_vars": next_var, "clauses": clauses}
