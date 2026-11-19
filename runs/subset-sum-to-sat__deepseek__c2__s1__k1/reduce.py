"""Polynomial-time reduction from Subset Sum to SAT.

Instance of Subset Sum: {"numbers": [a1, a2, ...], "target": t} with
non-negative integers a_i and an arbitrary integer target t.

We introduce one boolean selection variable s_i per number.  A ripple-carry
adder circuit computes the binary value

        S = sum_i s_i * a_i

and unit clauses force S to equal t.  Every gate is Tseitin-encoded, so the
resulting CNF is equisatisfiable with the original instance.

The circuit has O(n * W) gates and clauses, where n is the number of numbers
and W is the bit length of sum(a_i).  Since W is polynomial in the input size
(the bit length of the numbers), the whole reduction is polynomial time.

Edge cases (handled directly):
  * t < 0  -> unsatisfiable formula.
  * t = 0  -> satisfiable formula (empty sub-list).
  * t > sum(numbers) -> unsatisfiable formula.
"""


def reduce(instance):
    numbers = instance["numbers"]
    target = instance["target"]

    # --- Edge cases from the problem statement -------------------------
    if target < 0:
        # No subset can sum to a negative target.
        return {"num_vars": 0, "clauses": [[]]}      # contains empty clause => no
    if target == 0:
        # The empty sub-list always works.
        return {"num_vars": 0, "clauses": []}        # no clauses => yes

    total = sum(numbers)
    if total < target:
        # All numbers are non-negative, so no subset can reach the target.
        return {"num_vars": 0, "clauses": [[]]}      # no

    # Here total > 0 and 0 < target <= total.
    W = total.bit_length()   # every partial sum fits in W bits

    # --- Tiny Tseitin circuit builder ----------------------------------
    class Circuit:
        def __init__(self):
            self.num_vars = 0
            self.clauses = []

        def new_var(self):
            self.num_vars += 1
            return self.num_vars

        def add_clause(self, lits):
            self.clauses.append(list(lits))

        def const(self, value):
            v = self.new_var()
            self.add_clause([v] if value else [-v])
            return v

        # z <-> a AND b
        def AND(self, a, b):
            z = self.new_var()
            self.add_clause([-z, a])
            self.add_clause([-z, b])
            self.add_clause([z, -a, -b])
            return z

        # z <-> a OR b
        def OR(self, a, b):
            z = self.new_var()
            self.add_clause([z, -a])
            self.add_clause([z, -b])
            self.add_clause([-z, a, b])
            return z

        # z <-> a XOR b
        def XOR(self, a, b):
            z = self.new_var()
            self.add_clause([-a, -b, -z])
            self.add_clause([a, b, -z])
            self.add_clause([a, -b, z])
            self.add_clause([-a, b, z])
            return z

    c = Circuit()
    true_lit = c.const(True)
    false_lit = -true_lit

    # Selection variables, one per number.
    select = [c.new_var() for _ in numbers]

    def majority(a, b, d):
        # (a AND b) OR (a AND d) OR (b AND d)
        return c.OR(c.OR(c.AND(a, b), c.AND(a, d)), c.AND(b, d))

    # Running sum bits, initially zero.
    run = [false_lit] * W

    for i, a in enumerate(numbers):
        # Bit j of the gated contribution is s_i if bit j of a is 1, else 0.
        g = [select[i] if (a >> j) & 1 else false_lit for j in range(W)]

        # Ripple-carry addition of g and run.
        carry = false_lit
        new_run = []
        for j in range(W):
            x, y = g[j], run[j]
            new_run.append(c.XOR(c.XOR(x, y), carry))
            carry = majority(x, y, carry)
        run = new_run

    # Force the computed sum bits to match the target bits.
    for j in range(W):
        if (target >> j) & 1:
            c.add_clause([run[j]])
        else:
            c.add_clause([-run[j]])

    return {"num_vars": c.num_vars, "clauses": c.clauses}
