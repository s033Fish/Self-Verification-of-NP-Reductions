"""Polynomial-time reduction from Subset Sum to SAT.

For an instance {"numbers": [a_1, ..., a_n], "target": t} we build a CNF
formula with one boolean variable x_i per number, meaning "a_i is chosen".
The formula encodes a ripple-carry adder circuit that computes

    sum_i x_i * a_i

bit by bit into an accumulator, and then forces every bit of the final
accumulator to equal the corresponding bit of t.

Each full adder is encoded by its truth table, using at most 8 clauses per
output, so the whole formula has O(n * W) variables and clauses, where W is
the bit length of sum(numbers) / t.  Since W is polynomial in the input
size, the reduction runs in polynomial time.

Edge cases:
  * t < 0            -> the empty clause (unsatisfiable).
  * t = 0            -> no clauses (satisfiable, empty sub-list).
  * t > sum(numbers) -> the empty clause (unsatisfiable).
"""

from itertools import product


def _add_gate(clauses, inputs, out, func):
    """Append CNF clauses enforcing ``out == func(*inputs)``.

    ``inputs`` is a list whose entries are either variable ids (positive
    ints) or Python ``bool`` constants.  ``out`` is a variable id.
    """
    var_positions = [k for k, inp in enumerate(inputs) if not isinstance(inp, bool)]
    for bits in product((False, True), repeat=len(var_positions)):
        assigned = {}
        for pos, bit in zip(var_positions, bits):
            assigned[pos] = bit
        vals = []
        for k, inp in enumerate(inputs):
            if isinstance(inp, bool):
                vals.append(inp)
            else:
                vals.append(assigned[k])
        expected = func(*vals)
        # Forbid: (all variable inputs equal vals) and (out != expected).
        clause = []
        for k, inp in enumerate(inputs):
            if isinstance(inp, bool):
                continue
            # Literal saying "input k differs from vals[k]".
            clause.append(-inp if vals[k] else inp)
        # Literal saying "out equals expected".
        clause.append(out if expected else -out)
        clauses.append(clause)


def _xor3(p, a, b):
    return bool(p) ^ bool(a) ^ bool(b)


def _majority(p, a, b):
    return (bool(p) + bool(a) + bool(b)) >= 2


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]
    n = len(numbers)

    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    if target > total:
        return {"num_vars": 0, "clauses": [[]]}

    # Enough bits to hold both the total and the target without overflow.
    W = max(total.bit_length(), target.bit_length()) + 1

    next_var = 1

    def new_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # x[i] is True iff numbers[i] is selected.
    x = [new_var() for _ in range(n)]

    # s[i][j] = bit j of the accumulator after adding the first i numbers.
    # s[0][j] is the constant False.
    s = [[False] * W for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(W):
            s[i][j] = new_var()

    # c[i][j] = carry into bit j while adding number i (c[i][0] = False).
    c = [[False] * W for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, W):
            c[i][j] = new_var()

    clauses = []
    for i in range(1, n + 1):
        a_i = numbers[i - 1]
        for j in range(W):
            # Addend bit is x_i when a_i has a 1 at position j, else 0.
            p = x[i - 1] if (a_i >> j) & 1 else False
            a = s[i - 1][j]
            b = c[i][j]
            _add_gate(clauses, [p, a, b], s[i][j], _xor3)
            if j + 1 < W:
                _add_gate(clauses, [p, a, b], c[i][j + 1], _majority)

    # Force the final accumulator to equal the target.
    for j in range(W):
        if (target >> j) & 1:
            clauses.append([s[n][j]])
        else:
            clauses.append([-s[n][j]])

    return {"num_vars": next_var - 1, "clauses": clauses}
