"""Helpers shared by the number problems.

Numbers are non-negative ints with no size limit, as reductions often build
very large numbers. Encoding size counts bits, so large values are not
mistaken for blowup when they are only polynomially long.
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import product

from .base import is_int, require


def validate_numbers(numbers: object) -> None:
    require(isinstance(numbers, list), "numbers must be a list")
    assert isinstance(numbers, list)
    for number in numbers:
        require(is_int(number), f"numbers must be ints, got {number!r}")
        require(number >= 0, f"numbers must be >= 0, got {number}")


def bits(value: int) -> int:
    return max(1, abs(value).bit_length())


def numbers_size(numbers: list[int]) -> int:
    return len(numbers) + sum(bits(number) for number in numbers)


def subset_sum_reachable(numbers: list[int], target: int) -> bool:
    """Exact, by one of two searches:

    * When few sums are possible (at most 2^16: few numbers or a small
      target), build the set of reachable sums up to `target`, one number
      at a time.
    * Otherwise a depth-first search over the numbers, largest first: take
      or skip each one, cut a branch as soon as the numbers left cannot
      reach what remains of the target, and remember (position, remainder)
      pairs already shown to fail. Instances from reductions (digits in a
      large base, as in 3-SAT -> Subset Sum) are settled in well under a
      second this way, where the set of sums would have ~2^40 members.
    """
    if target < 0:
        return False
    positive = sorted((x for x in numbers if x > 0), reverse=True)
    if target == 0:
        return True
    if sum(positive) < target:
        return False
    if min(1 << len(positive), target + 1) <= 1 << 16 or len(positive) > 800:
        sums = {0}
        for number in positive:
            sums |= {s + number for s in sums if s + number <= target}
            if target in sums:
                return True
        return target in sums

    left = [0] * (len(positive) + 1)  # left[i] = sum of positive[i:]
    for i in range(len(positive) - 1, -1, -1):
        left[i] = left[i + 1] + positive[i]
    failed: set[tuple[int, int]] = set()

    def search(i: int, remaining: int) -> bool:
        if remaining == 0:
            return True
        if left[i] < remaining or (i, remaining) in failed:
            return False
        if positive[i] <= remaining and search(i + 1, remaining - positive[i]):
            return True
        if search(i + 1, remaining):
            return True
        failed.add((i, remaining))
        return False

    return search(0, target)


def small_number_lists(scale: int, max_value: int = 3) -> Iterator[list[int]]:
    """Every list of length <= scale with values 0..max_value."""
    for length in range(scale + 1):
        for values in product(range(max_value + 1), repeat=length):
            yield list(values)