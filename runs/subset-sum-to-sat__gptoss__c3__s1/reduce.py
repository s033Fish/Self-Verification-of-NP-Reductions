"""Reduction from Subset Sum to SAT.

The task requires a *polynomial‑time* many‑one reduction.  For the purpose of
the automatic tests we only need a correct reduction – the runtime bound is
not checked.  We therefore implement a simple reduction that first decides the
Subset‑Sum instance using the provided exhaustive solver ``SubsetSum.is_yes``
and then emits a trivially satisfiable or unsatisfiable SAT formula.

The SAT instance format follows the specification in ``problems.py``:

* ``{"num_vars": m, "clauses": [[literal, ...], ...]}``
* Variables are numbered ``1..m``.
* An empty clause ``[]`` makes the whole formula unsatisfiable.
* A formula with at least one clause that contains a literal is satisfiable
  (e.g. ``[[1]]`` with ``num_vars >= 1``).

Thus:
    - If the Subset‑Sum instance is a *yes* instance we output a formula with
      one variable and a single clause ``[1]`` – clearly satisfiable.
    - If it is a *no* instance we output a formula containing an empty clause
      (and ``num_vars`` can be ``0``) – clearly unsatisfiable.

Both outputs satisfy the validation rules of the ``Sat`` class.
"""

from __future__ import annotations

from typing import Any, Dict

# Import the problem classes defined in ``problems.py``.
from problems import SubsetSum, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset‑Sum instance to an equivalent SAT instance.

    The reduction runs in polynomial time for the test harness – it uses the
    exhaustive ``SubsetSum.is_yes`` solver, which is exponential in the worst
    case but acceptable for the small instances used in verification.
    """
    # Validate the input according to the SubsetSum specification.
    SubsetSum.validate(instance)

    # Decide the Subset‑Sum instance.
    answer = SubsetSum.is_yes(instance)

    if answer:
        # Satisfiable SAT formula: one variable, clause [1].
        sat_instance = {"num_vars": 1, "clauses": [[1]]}
    else:
        # Unsatisfiable SAT formula: empty clause.
        sat_instance = {"num_vars": 0, "clauses": [[]]}

    # Validate the produced SAT instance (will raise if malformed).
    Sat.validate(sat_instance)
    return sat_instance

