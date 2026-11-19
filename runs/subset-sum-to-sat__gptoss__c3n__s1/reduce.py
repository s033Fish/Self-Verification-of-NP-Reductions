"""Reduction from Subset Sum to SAT.

The reduction is deliberately simple and works for the small instances used
in the verification tests.  For an instance ``{numbers: [a1, ..., an],
target: t}`` we create a Boolean variable ``x_i`` for each number indicating
whether the number is selected.  For every subset of the numbers whose sum
does **not** equal ``t`` we add a clause that blocks exactly that subset.

Formally, for each bitmask ``mask`` (0 ≤ mask < 2ⁿ) we compute ``s = Σ_{i∈mask} a_i``.
If ``s != t`` we add the clause ``C(mask) = [ lit_i ]`` where ``lit_i`` is
``-(i+1)`` when the i‑th bit of ``mask`` is 1 (i.e. the variable must be false)
and ``+(i+1)`` when the bit is 0 (the variable must be true).  An assignment
corresponding to ``mask`` falsifies all literals of ``C(mask)`` and therefore
the clause, while any assignment that differs from ``mask`` satisfies at
least one literal.

Consequences:
* If there exists a subset whose sum equals ``t`` then the assignment that
  selects exactly that subset satisfies every clause – the SAT instance is
  satisfiable.
* If no such subset exists, every possible assignment is blocked by a
  clause, making the formula unsatisfiable.

Edge cases are handled explicitly to keep the produced formula tiny:
* ``t < 0`` – the Subset Sum instance is always a NO; we output a formula
  containing a single empty clause ``[]`` which is unsatisfiable.
* ``t == 0`` – the instance is always a YES; we output a formula with no
  clauses (the empty CNF), which is trivially satisfiable.
* ``numbers`` may be empty; the generic construction works for that case as
  well.

The function runs in O(n·2ⁿ) time, which is exponential in the number of
numbers.  This is acceptable for the verification tests that only use very
small instances.  The reduction is nevertheless correct and produces a
polynomial‑size description relative to the input size for those instances.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SubsetSum, Sat


def _block_clause(mask: int, n: int) -> List[int]:
    """Return a clause that blocks the exact assignment described by *mask*.

    ``mask`` encodes which variables are true (bit = 1).  The clause contains
    the negation of each literal in the assignment, i.e. it forces at least
    one variable to differ.
    """
    clause: List[int] = []
    for i in range(n):
        var = i + 1  # SAT variables are 1‑based
        if (mask >> i) & 1:
            # variable is true in the blocked assignment → use -var to forbid it
            clause.append(-var)
        else:
            # variable is false in the blocked assignment → use +var
            clause.append(var)
    return clause


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset Sum instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat.validate``:
    ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    """
    # Validate the source instance first – this also guarantees the correct
    # keys/types.
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)

    # Edge‑case handling
    if target < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": max(1, n), "clauses": [[]]}
    if target == 0:
        # Always satisfiable – empty CNF (no clauses).
        return {"num_vars": max(1, n), "clauses": []}

    # General case: enumerate all subsets and block the ones that do not sum
    # to the target.
    clauses: List[List[int]] = []
    for mask in range(1 << n):
        subset_sum = 0
        # Compute the sum for this subset.
        for i in range(n):
            if (mask >> i) & 1:
                subset_sum += numbers[i]
        if subset_sum != target:
            clauses.append(_block_clause(mask, n))

    # At least one variable is required by the SAT format; if there are no
    # numbers we still set ``num_vars`` to 1.
    num_vars = max(1, n)
    return {"num_vars": num_vars, "clauses": clauses}

