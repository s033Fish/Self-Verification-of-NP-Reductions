"""Reduction from Subset Sum to SAT.

The source problem SubsetSum has instances of the form
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non‑negative integers and the target is an integer.

The target problem SAT expects a CNF formula represented as
    {"num_vars": m, "clauses": [[l1, l2, ...], ...]}
where each literal is a signed integer (positive for the variable, negative
for its negation).  The formula is satisfiable iff there exists an assignment
to the variables that makes every clause contain a true literal.

We construct a polynomial‑time many‑one reduction.  For each number we create
 a selection variable x_i that indicates whether the i‑th number is taken.
The goal is to enforce the equation
    Σ_i x_i * a_i = target.

The reduction builds a binary adder circuit that adds, for every bit position
 k, all selection variables whose corresponding number has a 1‑bit at k.  The
 circuit is expressed in CNF using auxiliary variables for XOR and AND gates.
Finally we force the resulting sum bits to equal the binary representation of
 the target.

The construction runs in time polynomial in the total number of bits of the
 input (i.e. O(n * B) where B is the maximum bit‑length of the numbers and the
 target).  No brute‑force solving of Subset Sum is performed.
"""

from typing import List, Dict, Any


def _xor_clauses(z: int, a: int, b: int) -> List[List[int]]:
    """Return CNF clauses encoding z = a XOR b.

    The truth table for XOR yields the four clauses:
        (¬a ∨ ¬b ∨ ¬z)
        (a ∨ b ∨ ¬z)
        (a ∨ ¬b ∨ z)
        (¬a ∨ b ∨ z)
    """
    return [
        [-a, -b, -z],
        [a, b, -z],
        [a, -b, z],
        [-a, b, z],
    ]


def _and_clauses(z: int, a: int, b: int) -> List[List[int]]:
    """Return CNF clauses encoding z = a ∧ b.

    The encoding:
        (¬a ∨ ¬b ∨ z)   (if a and b then z)
        (a ∨ ¬z)         (if z then a)
        (b ∨ ¬z)         (if z then b)
    """
    return [
        [-a, -b, z],
        [a, -z],
        [b, -z],
    ]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset Sum instance to a SAT instance.

    Returns a dictionary with keys ``num_vars`` and ``clauses`` as required by
    ``problems.py``.
    """
    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases
    if target == 0:
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Selection variables 1..n
    n = len(numbers)
    var_counter = n
    clauses: List[List[int]] = []

    # Bit‑width sufficient for total sum
    total_sum = sum(numbers)
    B = max(target.bit_length(), total_sum.bit_length()) + 1

    # bits[k] will hold the literals currently representing the k‑th bit of the sum.
    bits: List[List[int]] = [[] for _ in range(B + 2)]  # extra slot for carries

    # Initialise: each number contributes its selection variable to the bits where it has a 1.
    for idx, a in enumerate(numbers, start=1):
        for k in range(B + 1):
            if (a >> k) & 1:
                bits[k].append(idx)

    def fresh_var() -> int:
        nonlocal var_counter
        var_counter += 1
        return var_counter

    # Reduce each column to at most one literal using pairwise full‑adder (XOR+AND).
    for k in range(B + 1):
        while len(bits[k]) > 1:
            a = bits[k].pop()
            b = bits[k].pop()
            sum_var = fresh_var()
            carry_var = fresh_var()
            clauses.extend(_xor_clauses(sum_var, a, b))
            clauses.extend(_and_clauses(carry_var, a, b))
            bits[k].append(sum_var)
            bits[k + 1].append(carry_var)

    # Process possible carries beyond B.
    for k in range(B + 1, len(bits)):
        while len(bits[k]) > 1:
            a = bits[k].pop()
            b = bits[k].pop()
            sum_var = fresh_var()
            carry_var = fresh_var()
            clauses.extend(_xor_clauses(sum_var, a, b))
            clauses.extend(_and_clauses(carry_var, a, b))
            bits[k].append(sum_var)
            if k + 1 >= len(bits):
                bits.append([])
            bits[k + 1].append(carry_var)

    # Enforce that the remaining bits equal the target.
    for k in range(len(bits)):
        bit_val = (target >> k) & 1
        if bits[k]:
            lit = bits[k][0]
            clauses.append([lit] if bit_val else [-lit])
        else:
            if bit_val:
                # Need a 1 where none exists → unsatisfiable.
                clauses.append([])
            # else bit 0 with no literal is already satisfied.

    return {"num_vars": var_counter, "clauses": clauses}

