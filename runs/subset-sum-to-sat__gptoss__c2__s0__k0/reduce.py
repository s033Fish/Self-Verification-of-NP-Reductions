import math

def xor2_clauses(a, b, out):
    # out = a xor b
    return [
        [out, a, b],                # out ∨ a ∨ b
        [out, -a, -b],              # out ∨ ¬a ∨ ¬b
        [-out, a, -b],              # ¬out ∨ a ∨ ¬b
        [-out, -a, b],              # ¬out ∨ ¬a ∨ b
    ]

def and2_clauses(a, b, out):
    # out = a ∧ b
    return [
        [-out, a],                  # ¬out ∨ a
        [-out, b],                  # ¬out ∨ b
        [out, -a, -b],              # out ∨ ¬a ∨ ¬b
    ]

def xor3_clauses(a, b, c, out):
    # out = a xor b xor c (odd parity)
    # Using CNF for parity of three vars.
    return [
        [out, a, b, c],
        [out, -a, -b, -c],
        [-out, a, b, -c],
        [-out, a, -b, c],
        [-out, -a, b, c],
        [-out, -a, -b, -c],
    ]

def majority3_clauses(a, b, c, out):
    # out = majority(a,b,c) i.e., at least two true
    return [
        [-out, a, b],
        [-out, a, c],
        [-out, b, c],
        [out, -a, -b],
        [out, -a, -c],
        [out, -b, -c],
    ]

def full_adder_clauses(a, b, c, sum_out, carry_out):
    # sum_out = a xor b xor c, carry_out = majority(a,b,c)
    clauses = []
    clauses.extend(xor3_clauses(a, b, c, sum_out))
    clauses.extend(majority3_clauses(a, b, c, carry_out))
    return clauses

def reduce(instance):
    numbers = instance.get("numbers", [])
    t = instance.get("target", 0)
    # Edge cases
    if t == 0:
        # Always yes: empty formula (no clauses) is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if t < 0:
        # Always no: unsatisfiable formula with an empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if not numbers:
        # Empty list: yes only if t == 0 which handled above, otherwise no.
        return {"num_vars": 1, "clauses": [[]]}

    n = len(numbers)
    max_sum = sum(numbers)
    B = max(max_sum.bit_length(), t.bit_length())
    # Variable numbering starts at 1.
    var_counter = 1
    # Selector variables for each number.
    selector_vars = []
    for _ in range(n):
        selector_vars.append(var_counter)
        var_counter += 1

    # Collect literals that contribute to each bit position.
    bit_literals = [[] for _ in range(B)]
    for idx, a in enumerate(numbers):
        for j in range(B):
            if (a >> j) & 1:
                bit_literals[j].append(selector_vars[idx])

    # Carry literals per bit position (incoming carries).
    carry_in = [[] for _ in range(B + 1)]  # carry_in[0] is empty (no initial carry)
    clauses = []
    sum_bits = [None] * B  # variable representing the j-th bit of the sum.

    for j in range(B):
        literals = bit_literals[j] + carry_in[j]
        # Reduce using full adders until at most two literals remain.
        while len(literals) > 2:
            a = literals.pop()
            b = literals.pop()
            c = literals.pop()
            sum_var = var_counter
            var_counter += 1
            carry_var = var_counter
            var_counter += 1
            clauses.extend(full_adder_clauses(a, b, c, sum_var, carry_var))
            # Sum stays at this bit.
            literals.append(sum_var)
            # Carry goes to next bit.
            carry_in[j + 1].append(carry_var)
        # Now handle the remaining 0,1,2 literals.
        if len(literals) == 0:
            sum_bits[j] = None  # constant false
        elif len(literals) == 1:
            sum_bits[j] = literals[0]
        else:  # two literals
            a, b = literals
            sum_var = var_counter
            var_counter += 1
            carry_var = var_counter
            var_counter += 1
            clauses.extend(xor2_clauses(a, b, sum_var))
            clauses.extend(and2_clauses(a, b, carry_var))
            sum_bits[j] = sum_var
            carry_in[j + 1].append(carry_var)

    # After processing all bits, any remaining carries must be forced to false.
    # They appear in carry_in[B] (and possibly beyond if carries propagated).
    # We'll treat all carries in positions >= B as false.
    for extra_carry in carry_in[B]:
        clauses.append([-extra_carry])

    # Enforce that the computed sum bits equal the target bits.
    for j in range(B):
        target_bit = (t >> j) & 1
        sb = sum_bits[j]
        if target_bit == 1:
            if sb is None:
                # Need a true constant but we have false -> unsat.
                return {"num_vars": var_counter - 1, "clauses": [[]]}
            else:
                clauses.append([sb])
        else:
            if sb is None:
                continue
            else:
                clauses.append([-sb])

    return {"num_vars": var_counter - 1, "clauses": clauses}

# The module should expose only the reduce function.
__all__ = ["reduce"]
