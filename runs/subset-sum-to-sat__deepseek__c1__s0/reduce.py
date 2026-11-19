"""Polynomial-time reduction from Subset Sum to SAT.

Instance of Subset Sum: {"numbers": [a1, a2, ...], "target": t}.

We build a CNF formula with one boolean variable x_i per number, where x_i is
true exactly when a_i is included in the chosen sub-list.  A binary
ripple-carry adder accumulates the chosen numbers into a running sum, and the
final sum bits are constrained to equal the bits of the target.  Every gate is
encoded with Tseitin auxiliary variables, so the formula has size
O(n * L) where L is the bit length of the total sum, i.e. polynomial in the
input size.

The formula is satisfiable exactly when some sub-list sums to the target.
"""


def _new_var(state):
    state[0] += 1
    return state[0]


def _and(a, b, clauses, state):
    """Return a literal equivalent to a AND b (Tseitin encoding)."""
    if a is False or b is False:
        return False
    if a is True:
        return b
    if b is True:
        return a
    z = _new_var(state)
    clauses.append([-a, -b, z])
    clauses.append([a, -z])
    clauses.append([b, -z])
    return z


def _or(a, b, clauses, state):
    """Return a literal equivalent to a OR b (Tseitin encoding)."""
    if a is True or b is True:
        return True
    if a is False:
        return b
    if b is False:
        return a
    z = _new_var(state)
    clauses.append([a, b, -z])
    clauses.append([-a, z])
    clauses.append([-b, z])
    return z


def _not(a):
    if a is True:
        return False
    if a is False:
        return True
    return -a


def _xor(a, b, clauses, state):
    """Return a literal equivalent to a XOR b (Tseitin encoding)."""
    if a is True:
        return _not(b)
    if a is False:
        return b
    if b is True:
        return _not(a)
    if b is False:
        return a
    z = _new_var(state)
    clauses.append([-a, -b, -z])
    clauses.append([a, b, -z])
    clauses.append([a, -b, z])
    clauses.append([-a, b, z])
    return z


def _full_adder(a, b, carry, clauses, state):
    """Return (sum, carry_out) for the one-bit addition a + b + carry."""
    total = _xor(_xor(a, b, clauses, state), carry, clauses, state)
    carry_out = _or(
        _and(a, b, clauses, state),
        _or(
            _and(a, carry, clauses, state),
            _and(b, carry, clauses, state),
            clauses,
            state,
        ),
        clauses,
        state,
    )
    return total, carry_out


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # A negative target can never be reached.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Target zero is always reachable via the empty sub-list.
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    if total < target:
        return {"num_vars": 0, "clauses": [[]]}

    # Enough bits to represent every possible subset sum and the target.
    width = max(total.bit_length(), target.bit_length()) + 1

    clauses = []
    state = [0]

    # x_i is true iff numbers[i] is chosen.
    choose = [_new_var(state) for _ in numbers]

    # Running sum, initially zero (the constant False).
    running = [False] * width

    for index, number in enumerate(numbers):
        carry = False
        new_running = []
        for bit in range(width):
            addend = choose[index] if (number >> bit) & 1 else False
            bit_sum, carry = _full_adder(
                running[bit], addend, carry, clauses, state
            )
            new_running.append(bit_sum)
        # The running sum never overflows `width` bits, so the final carry
        # must be false.  (This is implied by the arithmetic; we state it.)
        if carry is True:
            clauses.append([])
        elif carry is not False:
            clauses.append([-carry])
        running = new_running

    # Force the final running sum to equal the target bit by bit.
    for bit in range(width):
        wanted = (target >> bit) & 1
        current = running[bit]
        if wanted:
            if current is True:
                continue
            if current is False:
                clauses.append([])
            else:
                clauses.append([current])
        else:
            if current is True:
                clauses.append([])
            elif current is False:
                continue
            else:
                clauses.append([-current])

    return {"num_vars": state[0], "clauses": clauses}
