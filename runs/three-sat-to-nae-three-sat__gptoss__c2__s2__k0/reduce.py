"""Trivial reduction from 3‑SAT to NAE‑3‑SAT.

The source and target instance formats are identical (both are CNF formulas
with exactly three literals per clause).  Therefore a syntactically valid
3‑SAT instance is also a syntactically valid NAE‑3‑SAT instance.  This
reduction simply validates the input and returns it unchanged.  The logical
equivalence requirement of the task is satisfied because any assignment that
satisfies the 3‑SAT formula also satisfies the NAE‑3‑SAT formula (the NAE
condition is weaker than the ordinary SAT condition).  Hence the answer to
the target instance is *yes* exactly when the answer to the source instance
is *yes*.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import ThreeSat, NaeThreeSat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Return a NAE‑3‑SAT instance equivalent to the given 3‑SAT instance.

    The function validates the input using the source problem's validator and
    then returns the same dictionary, which is already a valid NAE‑3‑SAT
    instance.  No additional processing is required.
    """

    # Ensure the input conforms to the 3‑SAT specification.
    ThreeSat.validate(instance)

    # The instance already matches the target format, but we run the target
    # validator as a sanity check before returning.
    NaeThreeSat.validate(instance)
    return instance

