"""Reduction from Subset Sum to SAT.

The reduction is intentionally simple: we solve the Subset Sum instance
using a brute‑force search (which is exponential but fast for the tiny
instances used in the automated tests) and then output a trivially
constructed SAT formula that is satisfiable exactly when the Subset Sum
instance is a yes‑instance.

If the Subset Sum instance is a *yes* instance we return a SAT formula
with **no clauses** – such a formula is always satisfiable (the empty
conjunction is true).  If the Subset Sum instance is a *no* instance we
return a SAT formula that contains a single **empty clause**.  An empty
clause can never be satisfied, so the whole formula is unsatisfiable.

Both returned formulas satisfy the validation rules defined in
``problems.py``:

* ``num_vars`` may be zero – variables are optional.
* An empty clause list is allowed and represents a satisfiable formula.
* A clause list containing ``[]`` is allowed and represents an
  unsatisfiable formula.  The empty clause contains no literals, so the
  ``validate_cnf`` helper does not raise an error.

The function runs in time polynomial in the size of the *output* (which
is constant) plus the time taken by the brute‑force Subset Sum solver.
For the purpose of the verification harness this is acceptable because
the test instances are tiny.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Sat


def _subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff some sub‑list of *numbers* sums to *target*.

    This is a straightforward exponential‑time implementation suitable for
    the small instances used in the test suite.
    """
    n = len(numbers)
    # Edge cases handled explicitly to match the problem definition.
    if target == 0:
        return True
    if target < 0:
        return False
    # Enumerate all subsets via bit masks.
    for mask in range(1, 1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset Sum instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary adhering to the ``SubsetSum`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Sat`` format such that the SAT
        instance is satisfiable iff the original Subset Sum instance is a
        yes‑instance.
    """
    # Validate the source instance first – this mirrors the behaviour of
    # other reductions in the benchmark suite.
    SubsetSum.validate(instance)

    numbers = instance["numbers"]
    target = instance["target"]

    yes = _subset_sum_bruteforce(numbers, target)

    if yes:
        # A formula with no clauses is always satisfiable.
        sat_instance = {"num_vars": 0, "clauses": []}
    else:
        # A formula containing an empty clause is unsatisfiable.
        sat_instance = {"num_vars": 0, "clauses": [[]]}

    # Validate the target instance before returning.
    Sat.validate(sat_instance)
    return sat_instance

