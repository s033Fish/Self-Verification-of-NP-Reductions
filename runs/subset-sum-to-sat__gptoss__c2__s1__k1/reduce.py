"""Reduction from Subset Sum to SAT (CNF).

The source problem (SubsetSum) instance format is a dictionary:
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non-negative integers and the target is an integer.

The target problem (Sat) expects a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are signed integers: a positive integer +v means variable v is true,
and a negative integer -v means variable v is false.  An empty list of
clauses denotes a trivially satisfiable formula; a clause that is the empty
list (i.e. ``[]``) makes the whole formula unsatisfiable.

This file implements a polynomial‑time many‑one reduction.  The idea is a
standard binary‑adder construction:

* For each number ``ai`` we introduce a Boolean variable ``xi`` that decides
  whether ``ai`` participates in the subset.
* We compute the binary sum of the selected numbers using a ripple‑carry
  adder built from half‑adders and full‑adders.  The adder introduces a linear
  number of auxiliary variables (``O(n·L)`` where ``L`` is the number of bits
  needed to represent the largest possible sum).
* Finally we force the resulting sum bits to equal the binary representation
  of the target value.

The construction respects all edge‑cases described in the problem
statements:

* ``target == 0`` → return an empty CNF (always satisfiable).
* ``target < 0`` → return a CNF containing a single empty clause (unsatisfiable).
* An empty list of numbers is handled automatically by the adder – the only
  way to satisfy the target‑equality clause is when ``target == 0``.

The reduction runs in time polynomial in the size of the input (the total
bit‑length of the numbers and the target).
"""

from __future__ import annotations

from typing import List, Dict, Optional, Tuple

def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"numbers": [...], "target": t}``

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[...], ...]}``
    """

    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge‑case handling ---------------------------------------------------
    if target == 0:
        # Empty formula is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        # Unsatisfiable – a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    n = len(numbers)
    # Number of bits needed for the largest possible sum (or target).
    max_sum = sum(numbers)
    L = max(max_sum, target).bit_length() + 1  # extra bit for overflow safety

    clauses: List[List[int]] = []
    var_counter = n  # variables 1..n are the selection variables x_i

    def new_var() -> int:
        nonlocal var_counter
        var_counter += 1
        return var_counter

    # Helper to add a clause.
    def add_clause(*lits: int) -> None:
        clauses.append(list(lits))

    # ---------------------------------------------------------------------
    # Basic Boolean gates in CNF (using auxiliary variables).
    # ---------------------------------------------------------------------
    def half_adder(a: int, b: int) -> Tuple[int, int]:
        """Return (sum, carry) where sum = a XOR b, carry = a AND b.
        Both ``a`` and ``b`` are variable indices (positive integers).
        """
        s = new_var()
        c = new_var()
        # sum = XOR
        add_clause(-a, -b, -s)   # ¬a ∨ ¬b ∨ ¬s
        add_clause(a, b, -s)     # a ∨ b ∨ ¬s
        add_clause(a, -b, s)     # a ∨ ¬b ∨ s
        add_clause(-a, b, s)     # ¬a ∨ b ∨ s
        # carry = AND
        add_clause(-a, -b, c)    # ¬a ∨ ¬b ∨ c
        add_clause(a, -c)        # a ∨ ¬c
        add_clause(b, -c)        # b ∨ ¬c
        return s, c

    def full_adder(a: int, b: int, c_in: int) -> Tuple[int, int]:
        """Return (sum, carry_out) for three input bits.
        Implements a + b + c_in.
        """
        # First half‑adder for a and b.
        s1, c1 = half_adder(a, b)
        # Second half‑adder adds the previous sum and the third input.
        s, c2 = half_adder(s1, c_in)
        # carry_out = c1 OR c2
        c_out = new_var()
        add_clause(-c1, c_out)   # ¬c1 ∨ c_out
        add_clause(-c2, c_out)   # ¬c2 ∨ c_out
        add_clause(c1, c2, -c_out)  # c1 ∨ c2 ∨ ¬c_out
        return s, c_out

    # ---------------------------------------------------------------------
    # Build the ripple‑carry adder that adds each selected number.
    # ---------------------------------------------------------------------
    # ``prev_bits[j]`` holds the variable representing the j‑th bit of the sum
    # after processing the previous numbers. ``None`` denotes the constant 0.
    prev_bits: List[Optional[int]] = [None] * L

    for idx, a in enumerate(numbers, start=1):
        xi = idx  # selection variable for this number
        new_bits: List[Optional[int]] = []
        carry_in: Optional[int] = None  # constant 0 at the start of each addition
        for j in range(L):
            term_bit = (a >> j) & 1
            term_var: Optional[int] = xi if term_bit else None

            # Determine which adder to use based on presence of variables.
            if term_var is None:
                # Adding only prev_bit and carry_in.
                a_bit = prev_bits[j]
                b_bit = carry_in
                if a_bit is None and b_bit is None:
                    sum_bit = None
                    carry_out = None
                elif a_bit is None:
                    sum_bit = b_bit
                    carry_out = None
                elif b_bit is None:
                    sum_bit = a_bit
                    carry_out = None
                else:
                    sum_bit, carry_out = half_adder(a_bit, b_bit)
            else:
                # term_var is xi (the selector). Add it together with prev_bit and carry.
                a_bit = prev_bits[j]
                b_bit = term_var
                c_bit = carry_in
                if a_bit is None and c_bit is None:
                    # sum = b_bit, no carry.
                    sum_bit = b_bit
                    carry_out = None
                elif a_bit is None:
                    # half‑adder of b_bit and c_bit
                    sum_bit, carry_out = half_adder(b_bit, c_bit)
                elif c_bit is None:
                    # half‑adder of a_bit and b_bit
                    sum_bit, carry_out = half_adder(a_bit, b_bit)
                else:
                    sum_bit, carry_out = full_adder(a_bit, b_bit, c_bit)
            new_bits.append(sum_bit)
            carry_in = carry_out
        # Discard any overflow carry beyond L bits (it would only affect higher
        # bits which we have allocated enough space for).
        prev_bits = new_bits

    # ---------------------------------------------------------------------
    # Constrain the final sum bits to equal the target.
    # ---------------------------------------------------------------------
    for j in range(L):
        target_bit = (target >> j) & 1
        bit_var = prev_bits[j]
        if target_bit == 1:
            if bit_var is None:
                # Constant 0 cannot equal 1 → unsatisfiable.
                return {"num_vars": var_counter, "clauses": [[]]}
            add_clause(bit_var)  # force true
        else:  # target_bit == 0
            if bit_var is not None:
                add_clause(-bit_var)  # force false
            # if bit_var is None it's already false.

    return {"num_vars": var_counter, "clauses": clauses}

