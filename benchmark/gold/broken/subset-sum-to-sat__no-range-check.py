"""BROKEN: Subset Sum -> SAT that compares only the low bits of the target.

SOURCE  Subset Sum  {"numbers": [a1, ...], "target": t}  yes iff some sub-list sums to t
TARGET  SAT         {"num_vars", "clauses"}  yes iff satisfiable

Construction: a binary adder circuit (Tseitin encoding).
  * Variable x_i = i + 1 means "number i is chosen".
  * Keep a running sum as W = total.bit_length() + 1 bits, starting at 0.
    For each i, add the bits of a_i that are switched on by x_i (bit b of
    a_i contributes x_i if that bit is 1, else 0) with a ripple-carry adder.
    Each XOR / AND / OR gate gets a fresh variable defined by 3-4 clauses;
    gates with a constant input are simplified away.
  * Force the final sum's bits to equal t's bits (unit clauses).

"""


def reduce(instance):
    numbers, t = instance["numbers"], instance["target"]
    total = sum(numbers)
    if t < 0:
        return {"num_vars": 0, "clauses": [[]]}
    # BUG: no t > total check, and only the low `width` bits of t are compared
    width = total.bit_length() + 1
    state = {"num_vars": len(numbers)}
    clauses = []

    def fresh():
        state["num_vars"] += 1
        return state["num_vars"]

    # A bit is a bool constant or a literal (a nonzero int). bool is checked
    # first: in Python, True and False are ints too.
    def neg(a):
        return (not a) if isinstance(a, bool) else -a

    def gate_and(a, b):
        if isinstance(a, bool):
            return b if a else False
        if isinstance(b, bool):
            return a if b else False
        g = fresh()
        clauses.extend([[-g, a], [-g, b], [g, -a, -b]])
        return g

    def gate_or(a, b):
        return neg(gate_and(neg(a), neg(b)))

    def gate_xor(a, b):
        if isinstance(a, bool):
            return neg(b) if a else b
        if isinstance(b, bool):
            return neg(a) if b else a
        g = fresh()
        clauses.extend([[-g, a, b], [-g, -a, -b], [g, -a, b], [g, a, -b]])
        return g

    running = [False] * width
    for i, a in enumerate(numbers):
        x = i + 1
        addend = [x if (a >> bit) & 1 else False for bit in range(width)]
        carry, out = False, []
        for bit in range(width):
            p = gate_xor(running[bit], addend[bit])
            out.append(gate_xor(p, carry))
            carry = gate_or(gate_and(running[bit], addend[bit]), gate_and(p, carry))
        running = out
    for bit in range(width):
        wanted = bool((t >> bit) & 1)
        value = running[bit]
        if isinstance(value, bool):
            if value != wanted:
                return {"num_vars": 0, "clauses": [[]]}
        else:
            clauses.append([value if wanted else -value])
    return {"num_vars": state["num_vars"], "clauses": clauses}