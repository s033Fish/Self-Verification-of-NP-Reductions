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
    """Exact: the set of subset sums up to `target`, built one number at a
    time. Its size is at most min(2^n, target + 1)."""
    if target < 0:
        return False
    sums = {0}
    for number in numbers:
        sums |= {s + number for s in sums if s + number <= target}
        if target in sums:
            return True
    return target in sums


def small_number_lists(scale: int, max_value: int = 3) -> Iterator[list[int]]:
    """Every list of length <= scale with values 0..max_value."""
    for length in range(scale + 1):
        for values in product(range(max_value + 1), repeat=length):
            yield list(values)
