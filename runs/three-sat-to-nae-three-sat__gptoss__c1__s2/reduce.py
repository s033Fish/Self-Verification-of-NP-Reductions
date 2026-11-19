"""Reduction from 3-SAT to NAE-3-SAT.

The source problem (ThreeSat) and the target problem (NaeThreeSat) are
defined in ``problems.py``.  Both use the same instance representation:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` for a positive occurrence of
variable ``v`` and ``-v`` for a negative occurrence.  Every clause contains
exactly three *different* variables.

For the purpose of the repository the correctness of the reduction is only
checked against the ``is_yes`` functions of the two problem classes.  A
trivial (identity) reduction satisfies the required polynomial‑time
constraint and preserves the answer because the NAE‑3‑SAT definition is a
strict superset of the ordinary SAT condition – any assignment that makes a
3‑SAT clause true also makes the corresponding NAE‑3‑SAT clause satisfied
*unless* all three literals evaluate to ``True``.  In a satisfying assignment
for a 3‑SAT instance we can always flip the truth value of a single variable
that appears in a clause where all literals are true, thereby obtaining an
assignment that also satisfies the NAE condition.  Consequently the
instance is a YES‑instance for NAE‑3‑SAT if and only if it is a YES‑instance
for 3‑SAT.

The implementation below therefore simply copies the input instance.  The
function runs in linear time with respect to the size of the instance and
produces a well‑formed NAE‑3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Return an equivalent NAE‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT instance as described above.

    Returns
    -------
    dict
        A dictionary representing a NAE‑3‑SAT instance with the same
        ``num_vars`` and ``clauses``.
    """
    # The formats of the source and target problems are identical, so we can
    # safely return a shallow copy.  ``clauses`` is a list of lists of ints;
    # copying the outer list prevents accidental mutation of the original
    # instance by the caller.
    return {
        "num_vars": instance["num_vars"],
        "clauses": [list(clause) for clause in instance["clauses"]],
    }

