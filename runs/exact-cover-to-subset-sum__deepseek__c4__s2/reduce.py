"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea (classic base encoding):
  Let the Exact Cover instance have universe {0, ..., u-1} and m sets.
  Pick a base B = m + 1 (strictly larger than the number of sets, so that
  when we add up at most m chosen set-numbers there can be no carry between
  base-B digits).

  For each set S_j build the integer
        a_j = sum_{i in S_j} B^i
  and set the target
        t = sum_{i=0}^{u-1} B^i        (digit 1 in every universe position).

  A sub-list of the a_j sums to t iff the corresponding sets are pairwise
  disjoint and cover every element exactly once:
    * Digit i of the sum equals the number of chosen sets containing i, which
      is at most m < B, so no carries occur and each digit is read directly.
    * The target has digit 1 in every position 0..u-1, so every element must
      be covered by exactly one chosen set.

  Edge cases:
    * u = 0: t = 0, and Subset Sum with target 0 is always yes (matches
      "u = 0 is yes").
    * Empty sets contribute the number 0, which never changes a sum, so they
      never matter (matches the source edge case).
    * Two copies of the same non-empty set give equal numbers; choosing both
      would put a 2 in some digit (no carry since 2 <= m < B), so the sum
      cannot equal t (matches "two copies can never both be chosen").

The integers produced have O(u * log(m+1)) bits, which is polynomial in the
input size, and all arithmetic is polynomial.
"""

from __future__ import annotations

from problems import ExactCover, SubsetSum


def reduce(instance: dict) -> dict:
    """Reduce an ExactCover instance to an equivalent SubsetSum instance."""
    ExactCover.validate(instance)

    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # Strictly greater than the maximum number of sets we could choose.
    base = num_sets + 1

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += base ** element
        numbers.append(value)

    target = 0
    for element in range(universe_size):
        target += base ** element

    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result
