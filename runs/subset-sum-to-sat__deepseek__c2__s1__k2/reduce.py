"""Polynomial-time reduction from Subset Sum to SAT.

Source instance:  {"numbers": [a1, a2, ...], "target": t}
Target instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Introduce one Boolean variable x_i for each number a_i, meaning "a_i is part
of the chosen sub-list".  We then build a binary ripple-carry adder circuit
that computes

        sum_i (a_i * x_i)

and add clauses forcing that sum to equal t.  The circuit is converted to CNF
with the standard Tseitin transformation (one auxiliary variable per gate,
clauses that exactly define each gate's output).

The adder has W bits, where W is one more than the number of bits needed for
max(sum(numbers), t).  Each of the n numbers contributes O(W) gates, so the
formula has O(n * W) variables and clauses -- polynomial in the input size
(which counts the bit lengths of the numbers and the target).

Edge cases
----------
* t < 0:  always "no".  We return the formula [[]] (an empty clause), which is
  unsatisfiable.
* t = 0:  always "yes" (empty sub-list).  We return the empty formula, which is
  satisfiable.
* Otherwise the general construction is used; if t exceeds sum(numbers) the
  equality clauses are unsatisfiable, as required.
"""


class _Cnf:
    """Tiny CNF builder with 1-based variables."""

    def __init__(self):
        self.num_vars = 0
        self.clauses = []

    def new_var(self):
        self.num_vars += 1
        return self.num_vars

    def add_clause(self, *literals):
        self.clauses.append(list(literals))


def _and(cnf, a, b):
    """Return a variable z with z == (a and b)."""
    z = cnf.new_var()
    cnf.add_clause(-z, a)
    cnf.add_clause(-z, b)
    cnf.add_clause(z, -a, -b)
    return z


def _xor(cnf, a, b):
    """Return a variable z with z == (a xor b)."""
    z = cnf.new_var()
    cnf.add_clause(-a, -b, -z)
    cnf.add_clause(a, b, -z)
    cnf.add_clause(a, -b, z)
    cnf.add_clause(-a, b, z)
    return z


def _majority(cnf, a, b, c):
    """Return a variable z with z == majority(a, b, c)."""
    z = cnf.new_var()
    cnf.add_clause(-a, -b, z)
    cnf.add_clause(-a, -c, z)
    cnf.add_clause(-b, -c, z)
    cnf.add_clause(a, b, -z)
    cnf.add_clause(a, c, -z)
    cnf.add_clause(b, c, -z)
    return z


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # t < 0 is always no: an unsatisfiable formula.
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # t = 0 is always yes: the empty sub-list works.  Empty formula is SAT.
    if target == 0:
        return {"num_vars": 0, "clauses": []}

    total = sum(numbers)
    # One extra bit gives room for carries; W covers every bit of target too.
    width = max(total.bit_length(), target.bit_length()) + 1

    cnf = _Cnf()

    # Selection variables x_i.
    x = [cnf.new_var() for _ in range(len(numbers))]

    # A variable pinned to False, used for constant 0 bits.
    false_var = cnf.new_var()
    cnf.add_clause(-false_var)

    # Running sum, initially 0.
    current = [false_var] * width

    for i, value in enumerate(numbers):
        # Addend bits: value's bit k gated by x_i (0 when x_i is false).
        addend = [x[i] if (value >> k) & 1 else false_var for k in range(width)]

        carry = false_var
        nxt = []
        for k in range(width):
            s = current[k]
            g = addend[k]
            # sum bit = s xor g xor carry
            partial = _xor(cnf, s, g)
            nxt.append(_xor(cnf, partial, carry))
            # carry = majority(s, g, carry)
            carry = _majority(cnf, s, g, carry)
        current = nxt

    # Force the final sum to equal target, bit by bit.
    for k in range(width):
        bit = current[k]
        if (target >> k) & 1:
            cnf.add_clause(bit)      # this sum bit must be true
        else:
            cnf.add_clause(-bit)     # this sum bit must be false

    return {"num_vars": cnf.num_vars, "clauses": cnf.clauses}
