def reduce(instance):
    """Polynomial-time reduction from Subset Sum to SAT.

    The returned CNF formula is satisfiable exactly when some sub-list of
    ``instance["numbers"]`` sums to ``instance["target"]``.

    Construction: each usable number a_i gets a selection variable x_i.
    A ripple-carry binary adder circuit is encoded with Tseitin variables
    for the sum and carry bits.  The final sum bits are forced to equal the
    bits of the target.  The circuit has O(n * B) variables and clauses,
    where n is the number of numbers and B is the bit length of their sum.
    """
    numbers = instance["numbers"]
    target = instance["target"]

    # t < 0 is always no.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # t = 0 is always yes (empty sub-list).
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    # target > 0.  Only numbers a with 0 < a <= target can participate in a
    # subset summing to target; zeros never matter and numbers larger than
    # target would overshoot (all numbers are non-negative).
    nums = [a for a in numbers if 0 < a <= target]
    total = sum(nums)

    # If even all usable numbers cannot reach the target, the answer is no.
    if total < target:
        return {"num_vars": 0, "clauses": [[]]}

    # Enough bits to hold any sum of nums.  Since total < 2**B, no overflow
    # can occur.
    B = total.bit_length() + 1

    next_var = 1
    clauses = []

    def new_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    def neg(sig):
        """Negate a signal: a bool constant or an int literal."""
        if isinstance(sig, bool):
            return not sig
        return -sig

    def add_clause(lits):
        """Add a clause, simplifying bool constants, duplicates and
        tautologies.  An empty simplified clause is stored as []."""
        seen = set()
        simplified = []
        for lit in lits:
            if isinstance(lit, bool):
                if lit:
                    return  # clause already satisfied by a True constant
                continue  # False constant disappears
            # lit is an int literal
            if -lit in seen:
                return  # tautology
            if lit not in seen:
                seen.add(lit)
                simplified.append(lit)
        if not simplified:
            clauses.append([])
        else:
            clauses.append(simplified)

    def full_adder(A, Bsig, C):
        """Encode S = A xor B xor C and Cout = majority(A, B, C).

        A, Bsig, C may be int literals or bool constants.  S and Cout are
        fresh variables.
        """
        S = new_var()
        Cout = new_var()

        # S clauses (forbid every assignment where S differs from parity).
        add_clause([A, Bsig, C, -S])
        add_clause([A, Bsig, neg(C), S])
        add_clause([A, neg(Bsig), C, S])
        add_clause([A, neg(Bsig), neg(C), -S])
        add_clause([neg(A), Bsig, C, S])
        add_clause([neg(A), Bsig, neg(C), -S])
        add_clause([neg(A), neg(Bsig), C, -S])
        add_clause([neg(A), neg(Bsig), neg(C), S])

        # Cout clauses (Cout is true iff at least two inputs are true).
        add_clause([neg(A), neg(Bsig), Cout])
        add_clause([neg(A), neg(C), Cout])
        add_clause([neg(Bsig), neg(C), Cout])
        add_clause([A, Bsig, -Cout])
        add_clause([A, C, -Cout])
        add_clause([Bsig, C, -Cout])

        return S, Cout

    def add_number(acc, a, x):
        """Return a new accumulator representing acc + a * x.

        acc is a list of B signals (the current sum bits, least significant
        first).  x is a selection literal.  a is a non-negative integer.
        """
        carry = False
        new_acc = []
        for k in range(B):
            A = acc[k]
            bit = (a >> k) & 1
            Bsig = x if bit else False
            S, carry = full_adder(A, Bsig, carry)
            new_acc.append(S)
        # The final carry out must be zero (no overflow is possible).
        add_clause([neg(carry)])
        return new_acc

    # One selection variable per usable number.
    xs = [new_var() for _ in nums]

    # Start with sum zero.
    acc = [False] * B
    for a, x in zip(nums, xs):
        acc = add_number(acc, a, x)

    # Force the computed sum bits to equal the target bits.
    for k in range(B):
        if (target >> k) & 1:
            add_clause([acc[k]])
        else:
            add_clause([neg(acc[k])])

    return {"num_vars": next_var - 1, "clauses": clauses}
