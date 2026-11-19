"""Reduction from Partition to Subset Sum.

The source problem (Partition) expects an instance of the form::

    {"numbers": [a1, a2, ...]}

All numbers are non‑negative integers.  The answer is *yes* iff the multiset
can be split into two groups with equal sum.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

The answer is *yes* iff some sub‑list of the numbers sums exactly to ``t``.

The classic polynomial‑time reduction is to ask whether a subset sums to half
the total.  If the total sum ``S`` is even we set ``t = S // 2`` – a subset of
sum ``t`` corresponds exactly to a partition of equal halves.  If ``S`` is odd
there is no valid partition; we must therefore produce a SubsetSum instance
that is *always* a ``no`` instance.  Because all numbers are non‑negative, any
target larger than ``S`` is impossible, so we use ``t = S + 1``.

The reduction runs in linear time in the size of the input list and produces a
valid SubsetSum instance for all edge cases (empty list, zeros, etc.).
"""

from __future__ import annotations

from typing import Dict, List

# The type used by the benchmark framework for instances – a plain dict.
Instance = Dict[str, object]


def reduce(instance: Instance) -> Instance:
    """Convert a Partition instance to an equivalent SubsetSum instance.

    Parameters
    ----------
    instance:
        A Partition instance ``{"numbers": [...]}``.  The caller is
        responsible for providing a valid instance (the benchmark will call
        ``Partition.validate`` beforehand).

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` such that
        ``SubsetSum.is_yes`` returns the same truth value as
        ``Partition.is_yes`` for the original instance.
    """

    # Extract the list of numbers.  The benchmark guarantees the key exists.
    numbers: List[int] = instance["numbers"]  # type: ignore[assignment]

    # Compute the total sum – Python's built‑in ``sum`` works for arbitrarily
    # large non‑negative integers.
    total: int = sum(numbers)

    if total % 2 == 0:
        # Even total – a partition exists iff there is a subset summing to
        # half the total.
        target = total // 2
    else:
        # Odd total – Partition is always ``no``.  Choose a target that is
        # strictly larger than the maximum possible subset sum (which is
        # ``total``).  ``total + 1`` satisfies this and is a valid non‑negative
        # integer.
        target = total + 1

    # Return a fresh dictionary to avoid mutating the input.
    return {"numbers": list(numbers), "target": target}

