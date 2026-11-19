"""Polynomial-time reduction from Subset Sum to SAT (CNF).

Idea
----
Introduce one Boolean variable x_i for every number a_i, meaning "a_i is
picked".  The selected sum is  sum_i x_i * a_i.  We build a ripple-carry
binary adder circuit that computes this sum, using Tseitin variables for
the intermediate sum bits and carries, and then force the output bits to
equal the bits of the target.

All numbers are non-negative, so the sum of all numbers is an upper bound
on any reachable sum.  Choosing W = max(total, target).bit_length() + 1
bits guarantees that the whole computation fits in W bits (no overflow).
The circuit has O(n * W) gates, hence O(n * W) variables and clauses,
which is polynomial in the size of the input encoding.

Edge cases:
  * target < 0  -> unsatisfiable (empty clause).
  * target == 0 -> satisfiable (empty formula; the empty subset works).
  * total < target -> unsatisfiable.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # t < 0 is always no.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # t = 0 is always yes (empty sub-list).
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)

    # The target is above every reachable sum: unsatisfiable.
    if total < target:
        return {"num_vars": 0, "clauses": [[]]}

    # Number of bits needed to hold any reachable sum (and the target).
    W = max(total, target).bit_length() + 1

    clauses = []
    next_var = 1

    def new_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # --- Tseitin gate encodings -------------------------------------------
    # A "signal" is either a positive variable id (>= 1) or None, where
    # None stands for the constant false.  (Constant true is never needed.)

    def xor2(a, b):
        """Return a signal z with z = a XOR b."""
        if a is None and b is None:
            return None
        if a is None:
            return b
        if b is None:
            return a
        if a == b:
            return None  # a XOR a = 0
        z = new_var()
        clauses.append([a, b, -z])
        clauses.append([-a, -b, -z])
        clauses.append([a, -b, z])
        clauses.append([-a, b, z])
        return z

    def and2(a, b):
        """Return a signal z with z = a AND b."""
        if a is None or b is None:
            return None
        if a == b:
            return a
        z = new_var()
        clauses.append([-a, -b, z])
        clauses.append([a, -z])
        clauses.append([b, -z])
        return z

    def or_of(lits):
        """Return a signal z with z = OR(lits) (None entries = false)."""
        unique = []
        seen = set()
        for lit in lits:
            if lit is None or lit in seen:
                continue
            seen.add(lit)
            unique.append(lit)
        if not unique:
            return None
        if len(unique) == 1:
            return unique[0]
        z = new_var()
        # lit -> z
        for lit in unique:
            clauses.append([-lit, z])
        # z -> (lit_1 OR ... OR lit_k)
        clauses.append([-z] + unique)
        return z

    def full_adder(a, b, cin):
        """Return (sum, carry_out) for a + b + cin.

        sum      = a XOR b XOR cin
        carry    = majority(a, b, cin)
        """
        s = xor2(xor2(a, b), cin)
        p = and2(a, b)
        q = and2(a, cin)
        r = and2(b, cin)
        cout = or_of([p, q, r])
        return s, cout

    # --- Build the adder chain --------------------------------------------
    xs = [new_var() for _ in numbers]

    cur = [None] * W  # running sum, initially 0
    for i, num in enumerate(numbers):
        x = xs[i]
        carry = None  # carry into bit 0 is 0
        nxt = [None] * W
        for k in range(W):
            b = x if ((num >> k) & 1) else None
            s, carry = full_adder(cur[k], b, carry)
            nxt[k] = s
        # The running sum never exceeds total < 2**W, so no overflow.
        if carry is not None:
            clauses.append([-carry])
        cur = nxt

    # --- Force the final sum to equal the target --------------------------
    for k in range(W):
        if (target >> k) & 1:
            if cur[k] is None:
                clauses.append([])  # constant 0 cannot equal 1
            else:
                clauses.append([cur[k]])
        else:
            if cur[k] is not None:
                clauses.append([-cur[k]])

    return {"num_vars": next_var - 1, "clauses": clauses}
