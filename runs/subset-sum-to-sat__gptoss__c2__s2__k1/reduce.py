"""Reduction from Subset Sum to SAT.

The source problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

The target problem (Sat) expects a CNF formula represented as::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where each literal is an integer ``v`` (positive for the variable being
True, negative for it being False).  The reduction introduced below runs in
polynomial time and satisfies the following correctness guarantees:

* If ``t == 0`` the returned formula has *no* clauses – an empty CNF is
  trivially satisfiable, matching the fact that the empty sub‑list always
  solves the Subset‑Sum instance.
* If ``t < 0`` the returned formula contains a single empty clause ``[]`` –
  an empty clause is unsatisfiable, matching the fact that a negative target
  can never be achieved with non‑negative numbers.
* For all other instances the reduction builds a classic binary‑addition
  circuit that adds the selected numbers (chosen by Boolean variables ``x_i``)
  and forces the resulting binary sum to equal the target ``t``.  The circuit
  is encoded in CNF using a Tseitin‑style encoding of a full‑adder.  The
  construction uses ``O(n * B)`` auxiliary variables where ``n`` is the number
  of input numbers and ``B`` is the number of bits required to represent the
  total sum (which is at most ``log2(sum(numbers)) + 1``).  Hence the reduction
  is polynomial in the size of the input.

The implementation is self‑contained and does not rely on any external
libraries besides the Python standard library.
"""

from __future__ import annotations

from itertools import product
from typing import List, Dict, Any


def _lit(var: int, value: bool) -> int:
    """Return the integer literal representing ``var`` being ``value``.

    ``value == True``  → ``+var``
    ``value == False`` → ``-var``
    """
    return var if value else -var


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset‑Sum instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat`` in
    ``problems.py``.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge‑case handling ---------------------------------------------------
    if target == 0:
        # Empty CNF (no clauses) is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        # An empty clause makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}
    if not numbers:
        # No numbers and target != 0 → unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    n = len(numbers)
    max_sum = sum(numbers)
    # Number of bits needed to represent any possible sum (including target).
    B = max(max_sum, target).bit_length()

    # Counter for fresh variable IDs (SAT variables are 1‑based).
    var_counter = 0

    def new_var() -> int:
        nonlocal var_counter
        var_counter += 1
        return var_counter

    clauses: List[List[int]] = []

    # Selection variables: x_i is true iff numbers[i] is chosen.
    x_vars = [new_var() for _ in range(n)]

    # ``acc_bits[i][b]`` – variable representing the b‑th bit of the accumulator
    # after processing the first i numbers (0 ≤ i ≤ n).  For i == 0 the bits are
    # constant 0, represented by ``None``.
    acc_bits: List[List[int | None]] = [[None] * B]

    # Build the ripple‑carry adder for each number.
    for idx, a in enumerate(numbers, start=1):
        prev = acc_bits[-1]
        cur: List[int] = []
        carry_in: int | None = None  # No carry into the least‑significant bit.

        for b in range(B):
            a_bit = (a >> b) & 1
            # The addend for this bit is x_idx if the corresponding bit of ``a``
            # is 1, otherwise it is the constant 0.
            add_var = x_vars[idx - 1] if a_bit == 1 else None

            # Gather the three inputs to the full‑adder: previous accumulator bit,
            # the conditional addend bit, and the incoming carry.
            inputs: List[int] = []
            if prev[b] is not None:
                inputs.append(prev[b])
            if add_var is not None:
                inputs.append(add_var)
            if carry_in is not None:
                inputs.append(carry_in)

            # Output variables for sum and carry.
            sum_var = new_var()
            carry_out = new_var()
            cur.append(sum_var)

            # Encode the full‑adder truth table using a Tseitin‑style encoding.
            # For every possible assignment to the inputs we add a clause that
            # forces the outputs to the correct values.
            for assignment in product([0, 1], repeat=len(inputs)):
                total = sum(assignment)
                expected_sum = (total % 2) == 1
                expected_carry = total >= 2

                # Clause for the sum output.
                clause_sum: List[int] = []
                for var, val in zip(inputs, assignment):
                    # Literal is false exactly when the variable takes the value
                    # ``val``; therefore we add the *negated* literal.
                    clause_sum.append(-var if val else var)
                clause_sum.append(_lit(sum_var, expected_sum))
                clauses.append(clause_sum)

                # Clause for the carry output.
                clause_carry: List[int] = []
                for var, val in zip(inputs, assignment):
                    clause_carry.append(-var if val else var)
                clause_carry.append(_lit(carry_out, expected_carry))
                clauses.append(clause_carry)

            # Prepare carry for the next more‑significant bit.
            carry_in = carry_out

        # After processing all bits, any overflow carry must be false.
        if carry_in is not None:
            clauses.append([-carry_in])
        acc_bits.append(cur)  # type: ignore[arg-type]

    # The final accumulator bits represent the sum of the selected numbers.
    final_bits = acc_bits[-1]
    for b, var in enumerate(final_bits):
        bit_val = ((target >> b) & 1) == 1
        # Force each bit to match the target.
        clauses.append([_lit(var, bit_val)])

    return {"num_vars": var_counter, "clauses": clauses}

