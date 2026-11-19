def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # Negative target is always no.
    if target < 0:
        return {"num_vars": 1, "clauses": [[]]}

    max_sum = sum(numbers)

    # Target larger than the sum of all numbers is always no.
    if target > max_sum:
        return {"num_vars": 1, "clauses": [[]]}

    # Number of bits needed to represent any subset sum.
    B = max(1, max_sum.bit_length())

    next_var = 1
    clauses = []

    def new_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    def add_clause(*lits):
        clauses.append(list(lits))

    def neg(w):
        if w is True:
            return False
        if w is False:
            return True
        return -w

    def and2(a, b):
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        if a == b:
            return a
        if a == -b:
            return False
        z = new_var()
        add_clause(neg(a), neg(b), z)
        add_clause(a, -z)
        add_clause(b, -z)
        return z

    def or2(a, b):
        if a is True or b is True:
            return True
        if a is False:
            return b
        if b is False:
            return a
        if a == b:
            return a
        if a == -b:
            return True
        z = new_var()
        add_clause(a, b, -z)
        add_clause(neg(a), z)
        add_clause(neg(b), z)
        return z

    def xor2(a, b):
        if a is False:
            return b
        if b is False:
            return a
        if a is True:
            return neg(b)
        if b is True:
            return neg(a)
        if a == b:
            return False
        if a == -b:
            return True
        z = new_var()
        add_clause(neg(a), neg(b), -z)
        add_clause(a, b, -z)
        add_clause(a, neg(b), z)
        add_clause(neg(a), b, z)
        return z

    def majority3(a, b, c):
        if a is True:
            return or2(b, c)
        if b is True:
            return or2(a, c)
        if c is True:
            return or2(a, b)
        if a is False:
            return and2(b, c)
        if b is False:
            return and2(a, c)
        if c is False:
            return and2(a, b)
        if a == b:
            return a
        if a == c:
            return a
        if b == c:
            return b
        if a == -b:
            return c
        if a == -c:
            return b
        if b == -c:
            return a
        z = new_var()
        add_clause(neg(a), neg(b), z)
        add_clause(neg(a), neg(c), z)
        add_clause(neg(b), neg(c), z)
        add_clause(a, b, -z)
        add_clause(a, c, -z)
        add_clause(b, c, -z)
        return z

    # Selection variables: x[i] is true iff numbers[i] is chosen.
    x = [new_var() for _ in numbers]

    # Accumulator bits, initially all zero.
    acc = [False] * B

    for i, a in enumerate(numbers):
        carry = False
        xi = x[i]
        for j in range(B):
            bit = xi if ((a >> j) & 1) else False
            t = xor2(acc[j], bit)
            s = xor2(t, carry)
            c = majority3(acc[j], bit, carry)
            acc[j] = s
            carry = c
        # No overflow is possible because B bits are enough for max_sum.
        if carry is True:
            add_clause()
        elif carry is not False:
            add_clause(-carry)

    # Force the accumulator bits to equal the target bits.
    for j in range(B):
        tbit = (target >> j) & 1
        w = acc[j]
        if tbit == 1:
            if w is False:
                add_clause()
            elif w is not True:
                add_clause(w)
        else:
            if w is True:
                add_clause()
            elif w is not False:
                add_clause(-w)

    # Ensure num_vars is at least 1 (harmless dummy variable if needed).
    if next_var == 1:
        new_var()

    return {"num_vars": next_var - 1, "clauses": clauses}
