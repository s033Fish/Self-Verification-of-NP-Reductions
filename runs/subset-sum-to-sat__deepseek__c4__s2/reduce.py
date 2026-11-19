"""Polynomial-time reduction from Subset Sum to SAT.

Idea
----
A subset of ``numbers`` is chosen by one boolean variable ``x_i`` per position.
The chosen sum ``sum_i x_i * a_i`` is computed by a ripple-carry binary adder
chain (one addition per number).  Each full adder is encoded in CNF by
forbidding every input assignment that would make an output wrong.  Finally the
accumulator bits are constrained to the binary representation of ``target``.

The circuit has O(n * L) gates, where n is the number of values and L is the
bit length of their total sum, so the reduction is polynomial in the input size.
"""

from itertools import product


def _unsat():
    # An empty clause can never be satisfied.
    return {"num_vars": 0, "clauses": [[]]}


def _sat():
    # No clauses: trivially satisfiable.
    return {"num_vars": 0, "clauses": []}


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]

    # Edge cases from the Subset Sum definition.
    if target < 0:
        return _unsat()
    if target == 0:
        return _sat()

    total = sum(numbers)
    if target > total:
        return _unsat()

    # target >= 1 and target <= total, so total >= 1 and numbers is non-empty.
    # L bits are enough to hold any subset sum (and hence target).
    L = total.bit_length() + 1

    clauses = []
    next_var = 1

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    def add_gate(inputs, out, func):
        """Constrain ``out`` to equal ``func(*inputs)``.

        ``inputs`` is a list whose entries are either variable indices (ints)
        or boolean constants.  One clause is emitted per assignment of the
        variable inputs; it is violated exactly when the inputs take that
        assignment and ``out`` differs from the required value.
        """
        var_positions = [(k, sig) for k, sig in enumerate(inputs)
                         if isinstance(sig, int) and not isinstance(sig, bool)]
        for assign in product([False, True], repeat=len(var_positions)):
            full = list(inputs)
            for (k, _sig), val in zip(var_positions, assign):
                full[k] = val
            value = func(*full)
            clause = []
            for (_k, sig), val in zip(var_positions, assign):
                clause.append(-sig if val else sig)
            clause.append(out if value else -out)
            clauses.append(clause)

    def xor3(a, b, c):
        return bool(a) ^ bool(b) ^ bool(c)

    def majority3(a, b, c):
        return (bool(a) and bool(b)) or (bool(a) and bool(c)) or (bool(b) and bool(c))

    # Selection variables x_i.
    x = [fresh() for _ in range(len(numbers))]

    # Accumulator starts at 0 (constants).
    acc = [False] * L

    for i, a in enumerate(numbers):
        carry = False
        new_acc = []
        for j in range(L):
            p = acc[j]
            q = x[i] if ((a >> j) & 1) else False
            s_var = fresh()
            c_var = fresh()
            add_gate([p, q, carry], s_var, xor3)
            add_gate([p, q, carry], c_var, majority3)
            new_acc.append(s_var)
            carry = c_var
        acc = new_acc
        # The carry out of the top bit is always 0 for valid sums and is
        # functionally determined by the gates above, so it needs no clause.

    # Force the accumulator to equal target.
    for j in range(L):
        if (target >> j) & 1:
            clauses.append([acc[j]])
        else:
            clauses.append([-acc[j]])

    return {"num_vars": next_var - 1, "clauses": clauses}
