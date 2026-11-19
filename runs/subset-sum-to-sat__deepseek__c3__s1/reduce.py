"""Polynomial-time reduction from Subset Sum to SAT.

Instance of Subset Sum: {"numbers": [a1, ..., an], "target": t}, with all
ai >= 0 and t any integer.  We build a CNF whose variables are

  * x_1 .. x_n            : x_i means "number i is chosen",
  * auxiliary Tseitin variables for a binary ripple-carry adder network
    that computes S = sum_i a_i * x_i bit by bit.

The final clauses force the bits of S to equal the bits of t.  The circuit
has O(n * B) gates where B = bit_length(sum(numbers)), hence polynomially
many variables/clauses in the input size (n and the bit lengths of the
numbers/target).  No search over the (possibly exponentially large) target
is performed.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    total = sum(numbers)

    # ---- Edge cases -------------------------------------------------
    # t < 0 is always no; t > sum(numbers) is no (all numbers >= 0).
    if target < 0 or target > total:
        return {"num_vars": 0, "clauses": [[]]}  # empty clause: unsatisfiable
    # t == 0 is always yes (empty sub-list).
    if target == 0:
        return {"num_vars": 0, "clauses": []}    # no clauses: satisfiable

    # Now 0 < target <= total, so total > 0.
    B = max(1, total.bit_length())

    clauses = []
    counter = [0]

    def new_var():
        counter[0] += 1
        return counter[0]

    # Constant false variable F (unit clause -F).  TRUE literal = -F.
    F = new_var()
    clauses.append([-F])
    TRUE = -F
    FALSE = F

    # ---- Tseitin gate helpers (all take/return literals) ------------
    def AND(a, b):
        z = new_var()
        clauses.append([-a, -b, z])
        clauses.append([a, -z])
        clauses.append([b, -z])
        return z

    def XOR(a, b):
        z = new_var()
        clauses.append([a, b, z])
        clauses.append([-a, -b, z])
        clauses.append([a, -b, -z])
        clauses.append([-a, b, -z])
        return z

    def MAJ(a, b, c):
        z = new_var()
        clauses.append([-a, -b, z])
        clauses.append([-a, -c, z])
        clauses.append([-b, -c, z])
        clauses.append([a, b, -z])
        clauses.append([a, c, -z])
        clauses.append([b, c, -z])
        return z

    def FULL_ADDER(a, b, carry_in):
        s = XOR(XOR(a, b), carry_in)
        c = MAJ(a, b, carry_in)
        return s, c

    # ---- Selection variables ----------------------------------------
    x = [new_var() for _ in range(n)]

    # ---- Running sum, little-endian, initially 0 --------------------
    running = [FALSE] * B
    for i in range(n):
        value = numbers[i]
        xi = x[i]
        carry = FALSE
        new_running = []
        for j in range(B):
            bit = TRUE if (value >> j) & 1 else FALSE
            addend = AND(bit, xi)          # a_i's bit j if x_i, else 0
            s, carry = FULL_ADDER(running[j], addend, carry)
            new_running.append(s)
        running = new_running

    # ---- Force the sum to equal the target --------------------------
    for j in range(B):
        if (target >> j) & 1:
            clauses.append([running[j]])
        else:
            clauses.append([-running[j]])

    return {"num_vars": counter[0], "clauses": clauses}
